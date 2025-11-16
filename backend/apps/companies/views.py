"""
Views pour la gestion des compagnies
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q

from apps.companies.models import Company
from apps.companies.serializers import (
    CompanyCreateSerializer,
    CompanyDetailSerializer,
    CompanyUpdateSerializer,
    CompanyValidationSerializer,
    CompanyListSerializer,
    CompanyStatsSerializer
)
from apps.users.permissions import (
    IsCompagnie,
    IsAdminGlobal,
    CanManageCompany,
    CanValidateCompany
)
from apps.logs.models import ActivityLog
from utils.pagination import StandardResultsSetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class CompanyViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des compagnies"""
    
    queryset = Company.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'is_active', 'city']
    search_fields = ['name', 'email', 'registration_number', 'city']
    ordering_fields = ['name', 'created_at', 'total_revenue']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Retourner le serializer approprié selon l'action"""
        if self.action == 'create':
            return CompanyCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CompanyUpdateSerializer
        elif self.action == 'list':
            return CompanyListSerializer
        elif self.action == 'stats':
            return CompanyStatsSerializer
        return CompanyDetailSerializer
    
    def get_queryset(self):
        """Filtrer selon le rôle"""
        queryset = super().get_queryset()
        
        # Les admins voient toutes les compagnies
        if self.request.user.role == 'admin':
            return queryset.select_related('validated_by')
        
        # Les compagnies ne voient que leur propre profil
        if self.request.user.role == 'compagnie' and self.request.user.company:
            return queryset.filter(id=self.request.user.company.id)
        
        # Les autres voient seulement les compagnies approuvées et actives
        return queryset.filter(status=Company.APPROVED, is_active=True)
    
    def get_permissions(self):
        """Permissions dynamiques selon l'action"""
        if self.action == 'create':
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [CanManageCompany()]
        elif self.action in ['validate', 'reject', 'suspend']:
            return [CanValidateCompany()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        """Créer une compagnie et l'associer à l'utilisateur"""
        company = serializer.save()
        
        # Associer l'utilisateur à la compagnie
        self.request.user.company = company
        self.request.user.save()
        
        # Logger la création
        ActivityLog.objects.create(
            user=self.request.user,
            action=ActivityLog.COMPANY_CREATE,
            description=f"Création compagnie : {company.name}",
            details={
                'company_id': str(company.id),
                'company_name': company.name,
                'registration_number': company.registration_number
            },
            content_type='Company',
            object_id=str(company.id),
            severity=ActivityLog.SEVERITY_INFO
        )
    
    @action(detail=True, methods=['post'], url_path='validate')
    def validate_company(self, request, pk=None):
        """Valider ou rejeter une compagnie (admin seulement)"""
        company = self.get_object()
        serializer = CompanyValidationSerializer(data=request.data)
        
        if serializer.is_valid():
            new_status = serializer.validated_data['status']
            admin_notes = serializer.validated_data.get('admin_notes', '')
            commission_rate = serializer.validated_data.get('commission_rate')
            
            # Mettre à jour le statut
            company.status = new_status
            company.admin_notes = admin_notes
            company.validated_by = request.user
            company.validated_at = timezone.now()
            
            if commission_rate:
                company.commission_rate = commission_rate
            
            company.save()
            
            # Logger l'action
            action = ActivityLog.COMPANY_APPROVE if new_status == Company.APPROVED else ActivityLog.COMPANY_REJECT
            ActivityLog.objects.create(
                user=request.user,
                action=action,
                description=f"{'Approbation' if new_status == Company.APPROVED else 'Rejet'} compagnie : {company.name}",
                details={
                    'company_id': str(company.id),
                    'company_name': company.name,
                    'status': new_status,
                    'admin_notes': admin_notes
                },
                content_type='Company',
                object_id=str(company.id),
                severity=ActivityLog.SEVERITY_WARNING
            )
            
            # Créer une notification pour l'utilisateur
            from apps.notifications.models import Notification
            Notification.objects.create(
                user=company.users.filter(role='compagnie').first(),
                notification_type=Notification.EMAIL,
                category=Notification.COMPANY_APPROVED if new_status == Company.APPROVED else Notification.COMPANY_REJECTED,
                title=f"Compagnie {'approuvée' if new_status == Company.APPROVED else 'rejetée'}",
                message=f"Votre compagnie {company.name} a été {'approuvée' if new_status == Company.APPROVED else 'rejetée'}. {admin_notes}",
                metadata={'company_id': str(company.id)}
            )
            
            return Response({
                'message': f"Compagnie {'approuvée' if new_status == Company.APPROVED else 'rejetée'} avec succès",
                'company': CompanyDetailSerializer(company).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='suspend')
    def suspend(self, request, pk=None):
        """Suspendre une compagnie"""
        company = self.get_object()
        reason = request.data.get('reason', '')
        
        company.status = Company.SUSPENDED
        company.admin_notes = reason
        company.is_active = False
        company.save()
        
        # Logger l'action
        ActivityLog.objects.create(
            user=request.user,
            action=ActivityLog.COMPANY_SUSPEND,
            description=f"Suspension compagnie : {company.name}",
            details={
                'company_id': str(company.id),
                'reason': reason
            },
            content_type='Company',
            object_id=str(company.id),
            severity=ActivityLog.SEVERITY_CRITICAL
        )
        
        return Response({
            'message': 'Compagnie suspendue avec succès',
            'company': CompanyDetailSerializer(company).data
        })
    
    @action(detail=True, methods=['get'], url_path='stats')
    def stats(self, request, pk=None):
        """Statistiques d'une compagnie"""
        company = self.get_object()
        
        # Vérifier les permissions
        if request.user.role != 'admin' and request.user.company != company:
            return Response(
                {'error': 'Vous n\'avez pas accès à ces statistiques'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = CompanyStatsSerializer(company)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='pending', permission_classes=[IsAdminGlobal])
    def pending(self, request):
        """Liste des compagnies en attente de validation"""
        queryset = self.get_queryset().filter(status=Company.PENDING)
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = CompanyListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = CompanyListSerializer(queryset, many=True)
        return Response(serializer.data)
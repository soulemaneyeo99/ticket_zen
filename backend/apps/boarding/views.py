"""
Views pour la gestion de l'embarquement
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import transaction

from apps.boarding.models import BoardingPass
from apps.boarding.serializers import (
    BoardingPassCreateSerializer,
    BoardingPassDetailSerializer,
    BoardingPassListSerializer,
    OfflineBoardingSyncSerializer
)
from apps.users.permissions import CanScanTicket
from apps.logs.models import ActivityLog
from utils.pagination import StandardResultsSetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class BoardingPassViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion de l'embarquement"""
    
    queryset = BoardingPass.objects.all()
    permission_classes = [IsAuthenticated, CanScanTicket]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['scan_status', 'trip', 'boarding_agent', 'is_offline_scan']
    search_fields = ['ticket__ticket_number', 'ticket__passenger_first_name', 'ticket__passenger_last_name']
    ordering_fields = ['scanned_at']
    ordering = ['-scanned_at']
    
    def get_serializer_class(self):
        """Retourner le serializer approprié"""
        if self.action == 'create':
            return BoardingPassCreateSerializer
        elif self.action == 'list':
            return BoardingPassListSerializer
        elif self.action == 'sync_offline':
            return OfflineBoardingSyncSerializer
        return BoardingPassDetailSerializer
    
    def get_queryset(self):
        """Filtrer selon le rôle"""
        queryset = super().get_queryset().select_related(
            'ticket', 'ticket__trip', 'ticket__passenger', 'boarding_agent'
        )
        
        # Les admins voient tous les scans
        if self.request.user.role == 'admin':
            return queryset
        
        # Les compagnies voient les scans de leurs voyages
        if self.request.user.role == 'compagnie' and self.request.user.company:
            return queryset.filter(trip__company=self.request.user.company)
        
        # Les embarqueurs voient leurs propres scans et ceux de leur compagnie
        if self.request.user.role == 'embarqueur' and self.request.user.company:
            return queryset.filter(trip__company=self.request.user.company)
        
        return queryset.none()
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Scanner un QR code"""
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            boarding_pass = serializer.save()
            
            # Logger le scan
            ActivityLog.objects.create(
                user=request.user,
                action=ActivityLog.TICKET_SCAN,
                description=f"Scan ticket : {boarding_pass.ticket.ticket_number}",
                details={
                    'boarding_pass_id': str(boarding_pass.id),
                    'ticket_id': str(boarding_pass.ticket.id),
                    'ticket_number': boarding_pass.ticket.ticket_number,
                    'scan_status': boarding_pass.scan_status,
                    'is_offline': boarding_pass.is_offline_scan
                },
                content_type='BoardingPass',
                object_id=str(boarding_pass.id),
                severity=ActivityLog.SEVERITY_INFO if boarding_pass.is_valid_scan else ActivityLog.SEVERITY_WARNING,
                ip_address=self.get_client_ip(request)
            )
            
            return Response({
                'message': 'Scan effectué avec succès',
                'boarding_pass': BoardingPassDetailSerializer(boarding_pass).data,
                'is_valid': boarding_pass.is_valid_scan
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='sync-offline')
    def sync_offline(self, request):
        """Synchroniser les scans effectués hors ligne"""
        serializer = OfflineBoardingSyncSerializer(data=request.data)
        
        if serializer.is_valid():
            boarding_passes_data = serializer.validated_data['boarding_passes']
            
            synced_count = 0
            failed_count = 0
            errors = []
            
            for bp_data in boarding_passes_data:
                try:
                    # Créer le boarding pass avec les données offline
                    bp_serializer = BoardingPassCreateSerializer(
                        data=bp_data,
                        context={'request': request}
                    )
                    
                    if bp_serializer.is_valid():
                        boarding_pass = bp_serializer.save()
                        boarding_pass.synced_at = timezone.now()
                        boarding_pass.save()
                        synced_count += 1
                    else:
                        failed_count += 1
                        errors.append({
                            'data': bp_data,
                            'errors': bp_serializer.errors
                        })
                
                except Exception as e:
                    failed_count += 1
                    errors.append({
                        'data': bp_data,
                        'error': str(e)
                    })
            
            return Response({
                'message': 'Synchronisation terminée',
                'synced_count': synced_count,
                'failed_count': failed_count,
                'errors': errors if errors else None
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='my-scans')
    def my_scans(self, request):
        """Scans effectués par l'embarqueur connecté"""
        queryset = self.get_queryset().filter(boarding_agent=request.user)
        
        # Filtrer par date si fournie
        date_filter = request.query_params.get('date')
        if date_filter:
            try:
                from datetime import datetime
                date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                queryset = queryset.filter(scanned_at__date=date)
            except ValueError:
                pass
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = BoardingPassListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = BoardingPassListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='today')
    def today(self, request):
        """Scans d'aujourd'hui"""
        today = timezone.now().date()
        queryset = self.get_queryset().filter(scanned_at__date=today)
        
        # Statistiques
        total_scans = queryset.count()
        valid_scans = queryset.filter(scan_status=BoardingPass.VALID).count()
        invalid_scans = total_scans - valid_scans
        
        serializer = BoardingPassListSerializer(queryset, many=True)
        
        return Response({
            'date': today.isoformat(),
            'statistics': {
                'total_scans': total_scans,
                'valid_scans': valid_scans,
                'invalid_scans': invalid_scans
            },
            'scans': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='trip-scans')
    def trip_scans(self, request):
        """Scans pour un voyage spécifique"""
        trip_id = request.query_params.get('trip_id')
        
        if not trip_id:
            return Response(
                {'error': 'trip_id requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(trip_id=trip_id)
        
        serializer = BoardingPassListSerializer(queryset, many=True)
        return Response({
            'trip_id': trip_id,
            'total_scans': queryset.count(),
            'valid_scans': queryset.filter(scan_status=BoardingPass.VALID).count(),
            'scans': serializer.data
        })
    
    @staticmethod
    def get_client_ip(request):
        """Récupérer l'IP du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
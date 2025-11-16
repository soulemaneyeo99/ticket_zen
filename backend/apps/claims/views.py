"""
Views pour la gestion des réclamations
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from apps.claims.models import Claim, ClaimMessage
from apps.claims.serializers import (
    ClaimCreateSerializer,
    ClaimDetailSerializer,
    ClaimUpdateSerializer,
    ClaimListSerializer,
    ClaimMessageSerializer
)
from apps.users.permissions import CanManageClaim, IsAdminGlobal
from apps.logs.models import ActivityLog
from utils.pagination import StandardResultsSetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class ClaimViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des réclamations"""
    
    queryset = Claim.objects.all()
    permission_classes = [IsAuthenticated, CanManageClaim]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'priority', 'category', 'user', 'assigned_to']
    search_fields = ['subject', 'description']
    ordering_fields = ['created_at', 'priority', 'status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Retourner le serializer approprié"""
        if self.action == 'create':
            return ClaimCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ClaimUpdateSerializer
        elif self.action == 'list':
            return ClaimListSerializer
        return ClaimDetailSerializer
    
    def get_queryset(self):
        """Filtrer selon le rôle"""
        queryset = super().get_queryset().select_related(
            'user', 'ticket', 'trip', 'assigned_to'
        )
        
        # Les admins voient toutes les réclamations
        if self.request.user.role == 'admin':
            return queryset
        
        # Les autres voient uniquement leurs réclamations
        return queryset.filter(user=self.request.user)
    
    def get_permissions(self):
        """Permissions dynamiques"""
        if self.action in ['update', 'partial_update']:
            # Les admins peuvent modifier toutes les réclamations
            # Les utilisateurs peuvent modifier leurs propres réclamations (limité)
            return [IsAuthenticated()]
        return super().get_permissions()
    
    @action(detail=False, methods=['get'], url_path='my-claims')
    def my_claims(self, request):
        """Réclamations de l'utilisateur connecté"""
        queryset = self.get_queryset().filter(user=request.user)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ClaimListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ClaimListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='open', permission_classes=[IsAdminGlobal])
    def open_claims(self, request):
        """Réclamations ouvertes (admin)"""
        queryset = self.get_queryset().filter(
            status__in=[Claim.OPEN, Claim.IN_PROGRESS]
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ClaimListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ClaimListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='assign', permission_classes=[IsAdminGlobal])
    def assign(self, request, pk=None):
        """Assigner une réclamation à un admin"""
        claim = self.get_object()
        admin_id = request.data.get('admin_id')
        
        if not admin_id:
            return Response(
                {'error': 'admin_id requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from apps.users.models import User
        try:
            admin = User.objects.get(id=admin_id, role='admin')
        except User.DoesNotExist:
            return Response(
                {'error': 'Admin introuvable'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        claim.assigned_to = admin
        claim.status = Claim.IN_PROGRESS
        claim.save()
        
        return Response({
            'message': 'Réclamation assignée avec succès',
            'claim': ClaimDetailSerializer(claim).data
        })
    
    @action(detail=True, methods=['post'], url_path='resolve', permission_classes=[IsAdminGlobal])
    def resolve(self, request, pk=None):
        """Résoudre une réclamation"""
        claim = self.get_object()
        resolution_notes = request.data.get('resolution_notes', '')
        
        claim.status = Claim.RESOLVED
        claim.resolution_notes = resolution_notes
        claim.resolved_at = timezone.now()
        claim.save()
        
        # Logger l'action
        ActivityLog.objects.create(
            user=request.user,
            action=ActivityLog.ADMIN_ACTION,
            description=f"Résolution réclamation : {claim.subject}",
            details={
                'claim_id': str(claim.id),
                'resolution_notes': resolution_notes
            },
            content_type='Claim',
            object_id=str(claim.id),
            severity=ActivityLog.SEVERITY_INFO
        )
        
        # Notifier l'utilisateur
        from apps.notifications.models import Notification
        Notification.objects.create(
            user=claim.user,
            notification_type=Notification.EMAIL,
            category=Notification.GENERAL,
            title='Réclamation résolue',
            message=f'Votre réclamation "{claim.subject}" a été résolue. {resolution_notes}',
            metadata={'claim_id': str(claim.id)}
        )
        
        return Response({
            'message': 'Réclamation résolue avec succès',
            'claim': ClaimDetailSerializer(claim).data
        })
    
    @action(detail=True, methods=['post'], url_path='close', permission_classes=[IsAdminGlobal])
    def close(self, request, pk=None):
        """Fermer une réclamation"""
        claim = self.get_object()
        
        claim.status = Claim.CLOSED
        claim.closed_at = timezone.now()
        claim.save()
        
        return Response({
            'message': 'Réclamation fermée avec succès',
            'claim': ClaimDetailSerializer(claim).data
        })
    
    @action(detail=True, methods=['get'], url_path='messages')
    def messages(self, request, pk=None):
        """Messages d'une réclamation"""
        claim = self.get_object()
        
        # Vérifier les permissions
        if request.user.role != 'admin' and claim.user != request.user:
            return Response(
                {'error': 'Vous n\'avez pas accès à cette réclamation'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        messages = claim.messages.all().order_by('created_at')
        
        # Filtrer les messages internes si l'utilisateur n'est pas admin
        if request.user.role != 'admin':
            messages = messages.filter(is_internal=False)
        
        serializer = ClaimMessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='add-message')
    def add_message(self, request, pk=None):
        """Ajouter un message à une réclamation"""
        claim = self.get_object()
        
        # Vérifier les permissions
        if request.user.role != 'admin' and claim.user != request.user:
            return Response(
                {'error': 'Vous n\'avez pas accès à cette réclamation'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ClaimMessageSerializer(
            data={
                **request.data,
                'claim': claim.id
            },
            context={'request': request}
        )
        
        if serializer.is_valid():
            message = serializer.save()
            
            # Notifier l'autre partie
            if request.user.role == 'admin':
                # Notifier l'utilisateur
                from apps.notifications.models import Notification
                Notification.objects.create(
                    user=claim.user,
                    notification_type=Notification.EMAIL,
                    category=Notification.GENERAL,
                    title='Nouvelle réponse à votre réclamation',
                    message=f'Un administrateur a répondu à votre réclamation "{claim.subject}".',
                    metadata={'claim_id': str(claim.id)},
                    action_url=f'/claims/{claim.id}'
                )
            
            return Response({
                'message': 'Message ajouté avec succès',
                'claim_message': ClaimMessageSerializer(message).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
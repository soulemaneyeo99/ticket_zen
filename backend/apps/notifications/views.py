"""
Views pour la gestion des notifications
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from apps.notifications.models import Notification
from apps.notifications.serializers import (
    NotificationCreateSerializer,
    NotificationDetailSerializer,
    NotificationListSerializer,
    NotificationMarkAsReadSerializer
)
from apps.users.permissions import CanManageNotification, IsAdminGlobal
from utils.pagination import StandardResultsSetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des notifications"""
    
    queryset = Notification.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['notification_type', 'category', 'status', 'user']
    search_fields = ['title', 'message']
    ordering_fields = ['created_at', 'sent_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Retourner le serializer approprié"""
        if self.action == 'create':
            return NotificationCreateSerializer
        elif self.action == 'list':
            return NotificationListSerializer
        elif self.action == 'mark_as_read':
            return NotificationMarkAsReadSerializer
        return NotificationDetailSerializer
    
    def get_queryset(self):
        """Filtrer selon le rôle"""
        queryset = super().get_queryset()
        
        # Les admins voient toutes les notifications
        if self.request.user.role == 'admin':
            return queryset
        
        # Les autres voient uniquement leurs notifications
        return queryset.filter(user=self.request.user)
    
    def get_permissions(self):
        """Permissions dynamiques"""
        if self.action == 'create':
            return [IsAdminGlobal()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [CanManageNotification()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'], url_path='unread')
    def unread(self, request):
        """Notifications non lues de l'utilisateur"""
        queryset = self.get_queryset().filter(
            user=request.user,
            status__in=[Notification.PENDING, Notification.SENT]
        )
        
        serializer = NotificationListSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'notifications': serializer.data
        })
    
    @action(detail=False, methods=['post'], url_path='mark-as-read')
    def mark_as_read(self, request):
        """Marquer des notifications comme lues"""
        serializer = NotificationMarkAsReadSerializer(data=request.data)
        
        if serializer.is_valid():
            notification_ids = serializer.validated_data['notification_ids']
            
            # Marquer comme lu uniquement les notifications de l'utilisateur
            updated = Notification.objects.filter(
                id__in=notification_ids,
                user=request.user
            ).update(
                status=Notification.READ,
                read_at=timezone.now()
            )
            
            return Response({
                'message': f'{updated} notification(s) marquée(s) comme lue(s)',
                'updated_count': updated
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='mark-all-as-read')
    def mark_all_as_read(self, request):
        """Marquer toutes les notifications comme lues"""
        updated = Notification.objects.filter(
            user=request.user,
            status__in=[Notification.PENDING, Notification.SENT]
        ).update(
            status=Notification.READ,
            read_at=timezone.now()
        )
        
        return Response({
            'message': f'{updated} notification(s) marquée(s) comme lue(s)',
            'updated_count': updated
        })
    
    @action(detail=False, methods=['delete'], url_path='clear-all')
    def clear_all(self, request):
        """Supprimer toutes les notifications de l'utilisateur"""
        deleted_count, _ = Notification.objects.filter(
            user=request.user
        ).delete()
        
        return Response({
            'message': f'{deleted_count} notification(s) supprimée(s)',
            'deleted_count': deleted_count
        })
    
    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """Statistiques des notifications de l'utilisateur"""
        queryset = self.get_queryset().filter(user=request.user)
        
        stats = {
            'total': queryset.count(),
            'unread': queryset.filter(status__in=[Notification.PENDING, Notification.SENT]).count(),
            'read': queryset.filter(status=Notification.READ).count(),
            'failed': queryset.filter(status=Notification.FAILED).count(),
            'by_category': {}
        }
        
        # Statistiques par catégorie
        for category, label in Notification.CATEGORY_CHOICES:
            stats['by_category'][category] = {
                'label': label,
                'count': queryset.filter(category=category).count()
            }
        
        return Response(stats)
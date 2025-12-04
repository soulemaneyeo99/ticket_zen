"""
Views pour la gestion des logs d'activité (lecture seule)
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.logs.models import ActivityLog
from apps.logs.serializers import ActivityLogSerializer
from apps.users.permissions import IsAdminGlobal
from utils.pagination import StandardResultsSetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour la consultation des logs (lecture seule)"""
    
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated, IsAdminGlobal]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['action', 'severity', 'user', 'content_type']
    search_fields = ['description', 'ip_address']
    ordering_fields = ['created_at', 'severity']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'], url_path='recent')
    def recent(self, request):
        """Logs récents (dernières 24h)"""
        from datetime import timedelta
        from django.utils import timezone
        
        yesterday = timezone.now() - timedelta(days=1)
        queryset = self.get_queryset().filter(created_at__gte=yesterday)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='by-user')
    def by_user(self, request):
        """Logs par utilisateur"""
        user_id = request.query_params.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(user_id=user_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='critical')
    def critical(self, request):
        """Logs critiques"""
        queryset = self.get_queryset().filter(
            severity__in=[ActivityLog.SEVERITY_ERROR, ActivityLog.SEVERITY_CRITICAL]
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """Statistiques des logs"""
        from django.db.models import Count
        
        queryset = self.get_queryset()
        
        stats = {
            'total': queryset.count(),
            'by_action': {},
            'by_severity': {},
            'by_user': {}
        }
        
        # Par action
        action_stats = queryset.values('action').annotate(count=Count('id')).order_by('-count')[:10]
        for item in action_stats:
            stats['by_action'][item['action']] = item['count']
        
        # Par sévérité
        severity_stats = queryset.values('severity').annotate(count=Count('id'))
        for item in severity_stats:
            stats['by_severity'][item['severity']] = item['count']
        
        # Par utilisateur (top 10)
        user_stats = queryset.filter(user__isnull=False).values(
            'user__email'
        ).annotate(count=Count('id')).order_by('-count')[:10]
        for item in user_stats:
            stats['by_user'][item['user__email']] = item['count']
        
        return Response(stats)
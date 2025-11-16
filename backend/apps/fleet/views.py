"""
Views pour la gestion de la flotte
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from apps.fleet.models import Vehicle
from apps.fleet.serializers import (
    VehicleCreateSerializer,
    VehicleDetailSerializer,
    VehicleUpdateSerializer,
    VehicleListSerializer
)
from apps.users.permissions import IsApprovedCompagnie, CanManageVehicle
from utils.pagination import StandardResultsSetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class VehicleViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des véhicules"""
    
    queryset = Vehicle.objects.all()
    permission_classes = [IsAuthenticated, CanManageVehicle]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['vehicle_type', 'status', 'is_active', 'company']
    search_fields = ['registration_number', 'brand', 'model']
    ordering_fields = ['registration_number', 'created_at', 'total_trips']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Retourner le serializer approprié"""
        if self.action == 'create':
            return VehicleCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return VehicleUpdateSerializer
        elif self.action == 'list':
            return VehicleListSerializer
        return VehicleDetailSerializer
    
    def get_queryset(self):
        """Filtrer selon le rôle"""
        queryset = super().get_queryset().select_related('company')
        
        # Les admins voient tous les véhicules
        if self.request.user.role == 'admin':
            return queryset
        
        # Les compagnies voient leurs véhicules
        if self.request.user.role == 'compagnie' and self.request.user.company:
            return queryset.filter(company=self.request.user.company)
        
        # Les autres voient les véhicules actifs
        return queryset.filter(is_active=True, status=Vehicle.ACTIVE)
    
    def perform_create(self, serializer):
        """Créer un véhicule pour la compagnie"""
        serializer.save(company=self.request.user.company)
    
    @action(detail=True, methods=['post'], url_path='toggle-status')
    def toggle_status(self, request, pk=None):
        """Changer le statut du véhicule"""
        vehicle = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Vehicle.STATUS_CHOICES):
            return Response(
                {'error': 'Statut invalide'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        vehicle.status = new_status
        vehicle.save()
        
        return Response({
            'message': 'Statut mis à jour avec succès',
            'vehicle': VehicleDetailSerializer(vehicle).data
        })
    
    @action(detail=False, methods=['get'], url_path='available')
    def available(self, request):
        """Liste des véhicules disponibles"""
        queryset = self.get_queryset().filter(
            status=Vehicle.ACTIVE,
            is_active=True
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = VehicleListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = VehicleListSerializer(queryset, many=True)
        return Response(serializer.data)
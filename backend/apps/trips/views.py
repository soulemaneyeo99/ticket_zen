"""
Views pour la gestion des voyages
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.db.models import Q, Count, Sum, F
from datetime import datetime, timedelta

from apps.trips.models import Trip, City
from apps.trips.serializers import (
    TripCreateSerializer,
    TripDetailSerializer,
    TripUpdateSerializer,
    TripListSerializer,
    TripSearchSerializer,
    CitySerializer
)
from apps.users.permissions import IsApprovedCompagnie, CanManageTrip
from apps.logs.models import ActivityLog
from utils.pagination import StandardResultsSetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class TripViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des voyages"""
    
    queryset = Trip.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'is_active', 'company', 'departure_city', 'arrival_city']
    search_fields = ['departure_city__name', 'arrival_city__name', 'departure_location']
    ordering_fields = ['departure_datetime', 'base_price', 'created_at']
    ordering = ['departure_datetime']
    
    def get_serializer_class(self):
        """Retourner le serializer approprié"""
        if self.action == 'create':
            return TripCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TripUpdateSerializer
        elif self.action == 'list':
            return TripListSerializer
        elif self.action == 'search':
            return TripSearchSerializer
        return TripDetailSerializer
    
    def get_queryset(self):
        """Filtrer selon le rôle"""
        queryset = super().get_queryset().select_related(
            'company', 'vehicle', 'departure_city', 'arrival_city'
        ).prefetch_related('boarding_agents')
        
        # Les admins voient tous les voyages
        if self.request.user.role == 'admin':
            return queryset
        
        # Les compagnies voient leurs voyages
        if self.request.user.role == 'compagnie' and self.request.user.company:
            return queryset.filter(company=self.request.user.company)
        
        # Les embarqueurs voient les voyages assignés
        if self.request.user.role == 'embarqueur':
            return queryset.filter(
                Q(boarding_agents=self.request.user) |
                Q(company=self.request.user.company)
            ).distinct()
        
        # Les voyageurs voient les voyages actifs et futurs
        return queryset.filter(
            is_active=True,
            status=Trip.SCHEDULED,
            departure_datetime__gte=timezone.now()
        )
    
    def get_permissions(self):
        """Permissions dynamiques"""
        if self.action == 'create':
            return [IsApprovedCompagnie()]
        elif self.action in ['update', 'partial_update', 'destroy', 'cancel']:
            return [CanManageTrip()]
        elif self.action in ['list', 'retrieve', 'search']:
            return [AllowAny()] if self.action == 'search' else [IsAuthenticated()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        """Créer un voyage"""
        trip = serializer.save()
        
        # Logger la création
        ActivityLog.objects.create(
            user=self.request.user,
            action=ActivityLog.TRIP_CREATE,
            description=f"Création voyage : {trip.departure_city.name} → {trip.arrival_city.name}",
            details={
                'trip_id': str(trip.id),
                'departure': trip.departure_city.name,
                'arrival': trip.arrival_city.name,
                'departure_datetime': trip.departure_datetime.isoformat(),
                'price': str(trip.base_price)
            },
            content_type='Trip',
            object_id=str(trip.id),
            severity=ActivityLog.SEVERITY_INFO
        )
        
        # Incrémenter le compteur de voyages de la compagnie
        trip.company.total_trips += 1
        trip.company.save(update_fields=['total_trips'])
    
    @action(detail=False, methods=['post'], url_path='search', permission_classes=[AllowAny])
    def search(self, request):
        """Rechercher des voyages"""
        serializer = TripSearchSerializer(data=request.data)
        
        if serializer.is_valid():
            departure_city = serializer.validated_data['departure_city']
            arrival_city = serializer.validated_data['arrival_city']
            departure_date = serializer.validated_data['departure_date']
            passengers = serializer.validated_data.get('passengers', 1)
            
            # Gestion des fuseaux horaires
            current_tz = timezone.get_current_timezone()
            now = timezone.now()
            
            # Début et fin de la journée demandée
            start_of_day = timezone.make_aware(datetime.combine(departure_date, datetime.min.time()), current_tz)
            end_of_day = timezone.make_aware(datetime.combine(departure_date, datetime.max.time()), current_tz)
            
            # Si la date est aujourd'hui, on cherche à partir de maintenant
            # Sinon, on cherche toute la journée
            if departure_date == now.date():
                search_start = now
            else:
                search_start = start_of_day
                
            # Si la date est passée (mais validée par le serializer, donc c'est "hier" proche ou erreur), on ne renvoie rien
            if end_of_day < now:
                return Response([])

            queryset = Trip.objects.filter(
                departure_city_id=departure_city,
                arrival_city_id=arrival_city,
                departure_datetime__range=(search_start, end_of_day),
                status=Trip.SCHEDULED,
                is_active=True,
                available_seats__gte=passengers
            ).select_related('company', 'vehicle', 'departure_city', 'arrival_city').order_by('departure_datetime')
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = TripListSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = TripListSerializer(queryset, many=True)
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        """Annuler un voyage"""
        trip = self.get_object()
        reason = request.data.get('reason', '')
        
        if trip.status == Trip.CANCELLED:
            return Response(
                {'error': 'Ce voyage est déjà annulé'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if trip.status in [Trip.IN_PROGRESS, Trip.COMPLETED]:
            return Response(
                {'error': 'Ce voyage ne peut plus être annulé'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        trip.status = Trip.CANCELLED
        trip.notes = f"{trip.notes}\nAnnulation: {reason}"
        trip.save()
        
        # Logger l'annulation
        ActivityLog.objects.create(
            user=request.user,
            action=ActivityLog.TRIP_CANCEL,
            description=f"Annulation voyage : {trip.departure_city.name} → {trip.arrival_city.name}",
            details={
                'trip_id': str(trip.id),
                'reason': reason
            },
            content_type='Trip',
            object_id=str(trip.id),
            severity=ActivityLog.SEVERITY_WARNING
        )
        
        # Notifier les passagers avec tickets confirmés
        from apps.tickets.models import Ticket
        from apps.notifications.models import Notification
        
        tickets = Ticket.objects.filter(
            trip=trip,
            status=Ticket.CONFIRMED
        ).select_related('passenger')
        
        for ticket in tickets:
            # Changer le statut du ticket
            ticket.status = Ticket.CANCELLED
            ticket.cancelled_at = timezone.now()
            ticket.cancellation_reason = f"Voyage annulé par la compagnie: {reason}"
            ticket.save()
            
            # Créer une notification
            Notification.objects.create(
                user=ticket.passenger,
                notification_type=Notification.EMAIL,
                category=Notification.TRIP_CANCELLED,
                title='Voyage annulé',
                message=f"Votre voyage {trip.departure_city.name} → {trip.arrival_city.name} du {trip.departure_datetime.strftime('%d/%m/%Y à %H:%M')} a été annulé. Raison: {reason}",
                metadata={
                    'trip_id': str(trip.id),
                    'ticket_id': str(ticket.id)
                },
                recipient_email=ticket.passenger_email
            )
        
        return Response({
            'message': 'Voyage annulé avec succès',
            'trip': TripDetailSerializer(trip).data,
            'cancelled_tickets': tickets.count()
        })
    
    @action(detail=True, methods=['post'], url_path='assign-agents')
    def assign_agents(self, request, pk=None):
        """Assigner des embarqueurs au voyage"""
        trip = self.get_object()
        agent_ids = request.data.get('agent_ids', [])
        
        if not agent_ids:
            return Response(
                {'error': 'Veuillez fournir au moins un embarqueur'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from apps.users.models import User
        agents = User.objects.filter(
            id__in=agent_ids,
            role='embarqueur',
            company=trip.company
        )
        
        if agents.count() != len(agent_ids):
            return Response(
                {'error': 'Certains embarqueurs sont invalides ou n\'appartiennent pas à votre compagnie'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        trip.boarding_agents.set(agents)
        
        return Response({
            'message': 'Embarqueurs assignés avec succès',
            'assigned_agents': agents.count()
        })
    
    @action(detail=True, methods=['get'], url_path='available-seats')
    def available_seats(self, request, pk=None):
        """Récupérer les sièges disponibles"""
        trip = self.get_object()
        
        from apps.tickets.models import Ticket
        
        # Récupérer les sièges réservés
        reserved_seats = Ticket.objects.filter(
            trip=trip,
            status__in=[Ticket.PENDING, Ticket.CONFIRMED, Ticket.USED]
        ).values_list('seat_number', flat=True)
        
        # Récupérer la configuration des sièges du véhicule
        seat_map = trip.vehicle.get_seat_map()
        
        # Marquer les sièges réservés
        for seat in seat_map.get('seats', []):
            seat['is_available'] = str(seat['number']) not in reserved_seats
        
        return Response({
            'trip_id': str(trip.id),
            'total_seats': trip.total_seats,
            'available_seats': trip.available_seats,
            'seat_map': seat_map
        })
    
    @action(detail=False, methods=['get'], url_path='my-trips', permission_classes=[IsApprovedCompagnie])
    def my_trips(self, request):
        """Voyages de ma compagnie"""
        queryset = self.get_queryset().filter(company=request.user.company)
        
        # Filtrer par statut si fourni
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TripListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = TripListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='upcoming')
    def upcoming(self, request):
        """Voyages à venir"""
        queryset = self.get_queryset().filter(
            departure_datetime__gte=timezone.now(),
            status=Trip.SCHEDULED,
            is_active=True
        ).order_by('departure_datetime')[:20]
        
        serializer = TripListSerializer(queryset, many=True)
        return Response(serializer.data)


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les villes (lecture seule)"""
    
    queryset = City.objects.filter(is_active=True).order_by('name')
    serializer_class = CitySerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter]
    search_fields = ['name', 'country']
    
    @action(detail=False, methods=['get'], url_path='popular')
    def popular(self, request):
        """Villes les plus populaires (basé sur les voyages)"""
        from django.db.models import Q, Count
        
        cities = City.objects.filter(is_active=True).annotate(
            trip_count=Count('departures', filter=Q(departures__is_active=True)) + 
                      Count('arrivals', filter=Q(arrivals__is_active=True))
        ).order_by('-trip_count')[:10]
        
        serializer = CitySerializer(cities, many=True)
        return Response(serializer.data)
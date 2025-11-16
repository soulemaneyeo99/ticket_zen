"""
Views pour la configuration de la plateforme
"""
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta

from apps.core.models import PlatformSettings, FAQ, Banner
from apps.core.serializers import (
    PlatformSettingsSerializer,
    FAQSerializer,
    BannerSerializer,
    DashboardStatsSerializer
)
from apps.users.permissions import IsAdminGlobal, CanManagePlatformSettings
from utils.pagination import StandardResultsSetPagination


class PlatformSettingsViewSet(viewsets.ModelViewSet):
    """ViewSet pour les paramètres de la plateforme"""
    
    queryset = PlatformSettings.objects.all()
    serializer_class = PlatformSettingsSerializer
    permission_classes = [CanManagePlatformSettings]
    
    def list(self, request):
        """Récupérer les paramètres (singleton)"""
        settings = PlatformSettings.load()
        serializer = self.get_serializer(settings)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        """Mettre à jour les paramètres"""
        settings = PlatformSettings.load()
        serializer = self.get_serializer(settings, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response({
                'message': 'Paramètres mis à jour avec succès',
                'settings': serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FAQViewSet(viewsets.ModelViewSet):
    """ViewSet pour les FAQs"""
    
    queryset = FAQ.objects.filter(is_active=True).order_by('category', 'order')
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    
    def get_permissions(self):
        """Permissions dynamiques"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminGlobal()]
        return [AllowAny()]
    
    def retrieve(self, request, *args, **kwargs):
        """Incrémenter le compteur de vues lors de la consultation"""
        instance = self.get_object()
        instance.views += 1
        instance.save(update_fields=['views'])
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='by-category')
    def by_category(self, request):
        """FAQs groupées par catégorie"""
        category = request.query_params.get('category')
        
        if category:
            queryset = self.get_queryset().filter(category=category)
        else:
            queryset = self.get_queryset()
        
        serializer = self.get_serializer(queryset, many=True)
        
        # Grouper par catégorie
        grouped = {}
        for faq in serializer.data:
            cat = faq['category']
            if cat not in grouped:
                grouped[cat] = {
                    'category': cat,
                    'category_display': faq['category_display'],
                    'faqs': []
                }
            grouped[cat]['faqs'].append(faq)
        
        return Response(list(grouped.values()))


class BannerViewSet(viewsets.ModelViewSet):
    """ViewSet pour les bannières"""
    
    queryset = Banner.objects.all().order_by('order', '-created_at')
    serializer_class = BannerSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    
    def get_permissions(self):
        """Permissions dynamiques"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminGlobal()]
        return [AllowAny()]
    
    def get_queryset(self):
        """Filtrer les bannières actives pour les non-admins"""
        queryset = super().get_queryset()
        
        if self.request.user.is_authenticated and self.request.user.role == 'admin':
            return queryset
        
        # Filtrer les bannières visibles
        now = timezone.now()
        return queryset.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        )
    
    @action(detail=False, methods=['get'], url_path='active')
    def active(self, request):
        """Bannières actuellement actives"""
        queryset = self.get_queryset()
        
        # Filtrer par rôle si l'utilisateur est connecté
        if request.user.is_authenticated:
            queryset = queryset.filter(
                Q(target_role='') | Q(target_role=request.user.role)
            )
        else:
            queryset = queryset.filter(target_role='')
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='track-view')
    def track_view(self, request, pk=None):
        """Incrémenter le compteur de vues"""
        banner = self.get_object()
        banner.views += 1
        banner.save(update_fields=['views'])
        
        return Response({'message': 'Vue enregistrée'})
    
    @action(detail=True, methods=['post'], url_path='track-click')
    def track_click(self, request, pk=None):
        """Incrémenter le compteur de clics"""
        banner = self.get_object()
        banner.clicks += 1
        banner.save(update_fields=['clicks'])
        
        return Response({'message': 'Clic enregistré'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Statistiques pour le dashboard"""
    from apps.users.models import User
    from apps.companies.models import Company
    from apps.trips.models import Trip
    from apps.tickets.models import Ticket
    from apps.payments.models import Payment
    from apps.claims.models import Claim
    
    user = request.user
    today = timezone.now().date()
    first_day_of_month = today.replace(day=1)
    
    # Statistiques globales (admin)
    if user.role == 'admin':
        stats = {
            'total_users': User.objects.count(),
            'total_companies': Company.objects.filter(status=Company.APPROVED).count(),
            'total_trips': Trip.objects.count(),
            'total_tickets': Ticket.objects.count(),
            'total_revenue': Payment.objects.filter(
                status=Payment.SUCCESS
            ).aggregate(total=Sum('amount'))['total'] or 0,
            
            # Aujourd'hui
            'new_users_today': User.objects.filter(created_at__date=today).count(),
            'new_bookings_today': Ticket.objects.filter(created_at__date=today).count(),
            'revenue_today': Payment.objects.filter(
                status=Payment.SUCCESS,
                created_at__date=today
            ).aggregate(total=Sum('amount'))['total'] or 0,
            
            # Ce mois
            'new_users_this_month': User.objects.filter(created_at__gte=first_day_of_month).count(),
            'new_bookings_this_month': Ticket.objects.filter(created_at__gte=first_day_of_month).count(),
            'revenue_this_month': Payment.objects.filter(
                status=Payment.SUCCESS,
                created_at__gte=first_day_of_month
            ).aggregate(total=Sum('amount'))['total'] or 0,
            
            # Taux
            'booking_conversion_rate': 0,  # À calculer selon logique métier
            'average_ticket_price': Ticket.objects.filter(
                status=Ticket.CONFIRMED
            ).aggregate(avg=Avg('total_amount'))['avg'] or 0,
            
            # En attente
            'pending_companies': Company.objects.filter(status=Company.PENDING).count(),
            'open_claims': Claim.objects.filter(status__in=[Claim.OPEN, Claim.IN_PROGRESS]).count(),
        }
    
    # Statistiques compagnie
    elif user.role == 'compagnie' and user.company:
        company = user.company
        
        stats = {
            'total_trips': Trip.objects.filter(company=company).count(),
            'total_tickets_sold': Ticket.objects.filter(
                trip__company=company,
                status__in=[Ticket.CONFIRMED, Ticket.USED]
            ).count(),
            'total_revenue': Payment.objects.filter(
                company=company,
                status=Payment.SUCCESS
            ).aggregate(total=Sum('company_amount'))['total'] or 0,
            
            # Aujourd'hui
            'trips_today': Trip.objects.filter(
                company=company,
                departure_datetime__date=today
            ).count(),
            'bookings_today': Ticket.objects.filter(
                trip__company=company,
                created_at__date=today
            ).count(),
            'revenue_today': Payment.objects.filter(
                company=company,
                status=Payment.SUCCESS,
                created_at__date=today
            ).aggregate(total=Sum('company_amount'))['total'] or 0,
            
            # Ce mois
            'trips_this_month': Trip.objects.filter(
                company=company,
                departure_datetime__gte=first_day_of_month
            ).count(),
            'bookings_this_month': Ticket.objects.filter(
                trip__company=company,
                created_at__gte=first_day_of_month
            ).count(),
            'revenue_this_month': Payment.objects.filter(
                company=company,
                status=Payment.SUCCESS,
                created_at__gte=first_day_of_month
            ).aggregate(total=Sum('company_amount'))['total'] or 0,
            
            # Taux d'occupation moyen
            'average_occupancy_rate': Trip.objects.filter(
                company=company,
                status=Trip.COMPLETED
            ).annotate(
                occupancy=(F('total_seats') - F('available_seats')) * 100.0 / F('total_seats')
            ).aggregate(avg=Avg('occupancy'))['avg'] or 0,
            
            # Véhicules actifs
            'active_vehicles': company.vehicles.filter(is_active=True).count(),
            
            # Voyages à venir
            'upcoming_trips': Trip.objects.filter(
                company=company,
                departure_datetime__gte=timezone.now(),
                status=Trip.SCHEDULED
            ).count(),
        }
    
    # Statistiques embarqueur
    elif user.role == 'embarqueur' and user.company:
        from apps.boarding.models import BoardingPass
        
        stats = {
            'total_scans': BoardingPass.objects.filter(boarding_agent=user).count(),
            'scans_today': BoardingPass.objects.filter(
                boarding_agent=user,
                scanned_at__date=today
            ).count(),
            'valid_scans_today': BoardingPass.objects.filter(
                boarding_agent=user,
                scanned_at__date=today,
                scan_status=BoardingPass.VALID
            ).count(),
            'assigned_trips_today': Trip.objects.filter(
                boarding_agents=user,
                departure_datetime__date=today
            ).count(),
        }
    
    # Statistiques voyageur
    elif user.role == 'voyageur':
        stats = {
            'total_bookings': Ticket.objects.filter(passenger=user).count(),
            'upcoming_trips': Ticket.objects.filter(
                passenger=user,
                status__in=[Ticket.CONFIRMED, Ticket.PENDING],
                trip__departure_datetime__gte=timezone.now()
            ).count(),
            'completed_trips': Ticket.objects.filter(
                passenger=user,
                status=Ticket.USED
            ).count(),
            'total_spent': Payment.objects.filter(
                user=user,
                status=Payment.SUCCESS
            ).aggregate(total=Sum('amount'))['total'] or 0,
        }
    
    else:
        stats = {}
    
    serializer = DashboardStatsSerializer(data=stats)
    serializer.is_valid()
    
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAdminGlobal])
def export_data(request):
    """Exporter des données (CSV, Excel, PDF)"""
    export_type = request.data.get('type')  # 'tickets', 'payments', 'trips', etc.
    export_format = request.data.get('format', 'csv')  # 'csv', 'excel', 'pdf'
    date_from = request.data.get('date_from')
    date_to = request.data.get('date_to')
    
    if not export_type:
        return Response(
            {'error': 'Type d\'export requis'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Import des services d'export
    from utils.exports import ExportService
    
    export_service = ExportService()
    
    try:
        result = export_service.export_data(
            export_type=export_type,
            export_format=export_format,
            date_from=date_from,
            date_to=date_to,
            user=request.user
        )
        
        return Response({
            'message': 'Export généré avec succès',
            'file_url': result['file_url'],
            'filename': result['filename']
        })
    
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de l\'export : {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Endpoint de vérification de santé de l'API"""
    from django.db import connection
    
    # Vérifier la base de données
    try:
        connection.ensure_connection()
        db_status = 'ok'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    # Vérifier Redis
    try:
        from django.core.cache import cache
        cache.set('health_check', 'ok', 10)
        redis_status = 'ok' if cache.get('health_check') == 'ok' else 'error'
    except Exception as e:
        redis_status = f'error: {str(e)}'
    
    return Response({
        'status': 'ok',
        'timestamp': timezone.now().isoformat(),
        'database': db_status,
        'cache': redis_status,
        'version': '1.0.0'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def app_info(request):
    """Informations sur l'application"""
    return Response({
        'name': 'Ticket Zen API',
        'version': '1.0.0',
        'description': 'API complète pour la plateforme de billetterie digitale Ticket Zen',
        'endpoints': {
            'auth': '/api/v1/auth/',
            'users': '/api/v1/users/',
            'companies': '/api/v1/companies/',
            'trips': '/api/v1/trips/',
            'tickets': '/api/v1/tickets/',
            'payments': '/api/v1/payments/',
            'boarding': '/api/v1/boarding/',
            'notifications': '/api/v1/notifications/',
            'claims': '/api/v1/claims/',
            'docs': '/api/docs/',
            'schema': '/api/schema/'
        },
        'support_email': 'support@ticketzen.com',
        'support_phone': '+225XXXXXXXXXX'
    })
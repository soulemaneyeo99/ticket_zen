"""
Configuration des URLs principales
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)

# Import des ViewSets
from apps.users.views import AuthViewSet, UserViewSet
from apps.companies.views import CompanyViewSet
from apps.fleet.views import VehicleViewSet
from apps.trips.views import TripViewSet, CityViewSet
from apps.tickets.views import TicketViewSet
from apps.payments.views import PaymentViewSet
from apps.boarding.views import BoardingPassViewSet
from apps.notifications.views import NotificationViewSet
from apps.logs.views import ActivityLogViewSet
from apps.claims.views import ClaimViewSet
from apps.core.views import (
    PlatformSettingsViewSet,
    FAQViewSet,
    BannerViewSet,
    dashboard_stats,
    export_data,
    health_check,
    app_info
)

# Configuration du router
router = DefaultRouter()

# Enregistrement des ViewSets
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'users', UserViewSet, basename='user')
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'trips', TripViewSet, basename='trip')
router.register(r'cities', CityViewSet, basename='city')
router.register(r'tickets', TicketViewSet, basename='ticket')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'boarding', BoardingPassViewSet, basename='boarding')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'logs', ActivityLogViewSet, basename='log')
router.register(r'claims', ClaimViewSet, basename='claim')
router.register(r'settings', PlatformSettingsViewSet, basename='settings')
router.register(r'faqs', FAQViewSet, basename='faq')
router.register(r'banners', BannerViewSet, basename='banner')

from apps.trips.init_views import initialize_cities

urlpatterns = [
    # Admin Django
    path('admin/', admin.site.urls),
    
    # API v1
    path('api/v1/', include(router.urls)),
    
    # Endpoints supplémentaires
    path('api/v1/dashboard/stats/', dashboard_stats, name='dashboard-stats'),
    path('api/v1/export/', export_data, name='export-data'),
    path('api/v1/health/', health_check, name='health-check'),
    path('api/v1/info/', app_info, name='app-info'),
    
    # Endpoint temporaire pour initialiser les villes (à supprimer après usage)
    path('api/v1/init-cities/', initialize_cities, name='init-cities'),
    
    # Documentation Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Servir les fichiers média en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Django Debug Toolbar
    try:
        import debug_toolbar
        urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    except ImportError:
        pass
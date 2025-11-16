"""
Serializers pour la configuration de la plateforme
"""
from rest_framework import serializers
from apps.core.models import PlatformSettings, FAQ, Banner


class PlatformSettingsSerializer(serializers.ModelSerializer):
    """Serializer pour les paramètres de la plateforme"""
    
    class Meta:
        model = PlatformSettings
        fields = [
            'default_commission_rate', 'ticket_cancellation_deadline_hours',
            'send_email_notifications', 'send_sms_notifications',
            'trip_reminder_hours_before', 'payment_timeout_minutes',
            'min_ticket_price', 'max_ticket_price', 'qr_code_expiration_hours',
            'max_tickets_per_booking', 'allow_overbooking',
            'overbooking_percentage', 'maintenance_mode',
            'maintenance_message', 'support_email', 'support_phone',
            'updated_at', 'updated_by'
        ]
        read_only_fields = ['updated_at', 'updated_by']


class FAQSerializer(serializers.ModelSerializer):
    """Serializer pour les FAQs"""
    
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = FAQ
        fields = [
            'id', 'category', 'category_display', 'question',
            'answer', 'order', 'is_active', 'views',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'category_display', 'views', 'created_at', 'updated_at']


class BannerSerializer(serializers.ModelSerializer):
    """Serializer pour les bannières"""
    
    is_visible = serializers.BooleanField(read_only=True)
    click_through_rate = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Banner
        fields = [
            'id', 'title', 'description', 'image', 'link_url',
            'is_active', 'start_date', 'end_date', 'order',
            'target_role', 'views', 'clicks', 'is_visible',
            'click_through_rate', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'views', 'clicks', 'is_visible',
            'click_through_rate', 'created_at', 'updated_at'
        ]


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer pour les statistiques du dashboard"""
    
    # Statistiques globales
    total_users = serializers.IntegerField()
    total_companies = serializers.IntegerField()
    total_trips = serializers.IntegerField()
    total_tickets = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    
    # Statistiques par période
    new_users_today = serializers.IntegerField()
    new_bookings_today = serializers.IntegerField()
    revenue_today = serializers.DecimalField(max_digits=15, decimal_places=2)
    
    new_users_this_month = serializers.IntegerField()
    new_bookings_this_month = serializers.IntegerField()
    revenue_this_month = serializers.DecimalField(max_digits=15, decimal_places=2)
    
    # Taux
    booking_conversion_rate = serializers.FloatField()
    average_ticket_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    # Compagnies en attente
    pending_companies = serializers.IntegerField()
    
    # Réclamations ouvertes
    open_claims = serializers.IntegerField()
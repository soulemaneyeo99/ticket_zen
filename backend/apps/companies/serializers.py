"""
Serializers pour les compagnies
"""
from rest_framework import serializers
from apps.companies.models import Company
from apps.users.serializers import UserDetailSerializer


class CompanyCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer une compagnie"""
    
    class Meta:
        model = Company
        fields = [
            'name', 'registration_number', 'tax_id', 'email',
            'phone_number', 'address', 'city', 'country',
            'description', 'logo', 'license_document',
            'insurance_document'
        ]
    
    def validate_registration_number(self, value):
        """Vérifier l'unicité du numéro d'enregistrement"""
        if Company.objects.filter(registration_number=value).exists():
            raise serializers.ValidationError('Ce numéro d\'enregistrement existe déjà.')
        return value
    
    def validate_email(self, value):
        """Vérifier l'unicité de l'email"""
        if Company.objects.filter(email=value).exists():
            raise serializers.ValidationError('Cet email est déjà utilisé.')
        return value


class CompanyDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour une compagnie"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_approved = serializers.BooleanField(read_only=True)
    validated_by_details = UserDetailSerializer(source='validated_by', read_only=True)
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'slug', 'registration_number', 'tax_id',
            'email', 'phone_number', 'address', 'city', 'country',
            'description', 'logo', 'license_document', 'insurance_document',
            'status', 'status_display', 'is_active', 'is_approved',
            'commission_rate', 'total_trips', 'total_tickets_sold',
            'total_revenue', 'validated_at', 'validated_by_details',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'slug', 'status', 'status_display', 'is_approved',
            'total_trips', 'total_tickets_sold', 'total_revenue',
            'validated_at', 'validated_by_details', 'created_at',
            'updated_at'
        ]


class CompanyUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour mettre à jour une compagnie"""
    
    class Meta:
        model = Company
        fields = [
            'email', 'phone_number', 'address', 'city',
            'description', 'logo', 'license_document',
            'insurance_document'
        ]


class CompanyValidationSerializer(serializers.Serializer):
    """Serializer pour valider/rejeter une compagnie"""
    
    status = serializers.ChoiceField(
        choices=[Company.APPROVED, Company.REJECTED],
        required=True
    )
    admin_notes = serializers.CharField(required=False, allow_blank=True)
    commission_rate = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        min_value=0,
        max_value=100
    )


class CompanyListSerializer(serializers.ModelSerializer):
    """Serializer minimaliste pour liste de compagnies"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'slug', 'city', 'status', 'status_display',
            'is_active', 'logo', 'total_trips', 'created_at'
        ]


class CompanyStatsSerializer(serializers.ModelSerializer):
    """Serializer pour les statistiques d'une compagnie"""
    
    average_ticket_price = serializers.SerializerMethodField()
    occupancy_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'total_trips', 'total_tickets_sold',
            'total_revenue', 'commission_rate', 'average_ticket_price',
            'occupancy_rate'
        ]
    
    def get_average_ticket_price(self, obj):
        """Calcule le prix moyen des tickets"""
        if obj.total_tickets_sold > 0:
            return float(obj.total_revenue / obj.total_tickets_sold)
        return 0
    
    def get_occupancy_rate(self, obj):
        """Calcule le taux d'occupation moyen"""
        from apps.trips.models import Trip
        from django.db.models import Avg, F
        
        trips = Trip.objects.filter(company=obj, status=Trip.COMPLETED)
        if trips.exists():
            avg_rate = trips.annotate(
                rate=(F('total_seats') - F('available_seats')) * 100.0 / F('total_seats')
            ).aggregate(Avg('rate'))
            return round(avg_rate['rate__avg'] or 0, 2)
        return 0
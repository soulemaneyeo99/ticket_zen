"""
Serializers pour la flotte de véhicules
"""
from rest_framework import serializers
from apps.fleet.models import Vehicle


class VehicleCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un véhicule"""
    
    class Meta:
        model = Vehicle
        fields = [
            'vehicle_type', 'registration_number', 'brand', 'model',
            'year', 'color', 'total_seats', 'seat_configuration',
            'has_ac', 'has_wifi', 'has_tv', 'has_usb_ports',
            'has_toilet', 'photo_main', 'photo_interior',
            'insurance_expiry', 'technical_inspection_expiry'
        ]
    
    def validate_registration_number(self, value):
        """Vérifier l'unicité de l'immatriculation"""
        if Vehicle.objects.filter(registration_number=value).exists():
            raise serializers.ValidationError('Ce numéro d\'immatriculation existe déjà.')
        return value
    
    def validate_year(self, value):
        """Valider l'année du véhicule"""
        from django.utils import timezone
        current_year = timezone.now().year
        if value > current_year:
            raise serializers.ValidationError('L\'année ne peut pas être dans le futur.')
        if value < 1990:
            raise serializers.ValidationError('L\'année doit être supérieure à 1990.')
        return value


class VehicleDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour un véhicule"""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    vehicle_type_display = serializers.CharField(source='get_vehicle_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    seat_map = serializers.JSONField(source='get_seat_map', read_only=True)
    
    class Meta:
        model = Vehicle
        fields = [
            'id', 'company', 'company_name', 'vehicle_type',
            'vehicle_type_display', 'registration_number', 'brand',
            'model', 'year', 'color', 'total_seats', 'seat_configuration',
            'seat_map', 'has_ac', 'has_wifi', 'has_tv', 'has_usb_ports',
            'has_toilet', 'status', 'status_display', 'is_active',
            'is_available', 'photo_main', 'photo_interior',
            'insurance_expiry', 'technical_inspection_expiry',
            'last_maintenance_date', 'next_maintenance_date',
            'maintenance_notes', 'total_trips', 'total_km',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'company_name', 'vehicle_type_display',
            'status_display', 'is_available', 'seat_map',
            'total_trips', 'total_km', 'created_at', 'updated_at'
        ]


class VehicleUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour mettre à jour un véhicule"""
    
    class Meta:
        model = Vehicle
        fields = [
            'color', 'seat_configuration', 'has_ac', 'has_wifi',
            'has_tv', 'has_usb_ports', 'has_toilet', 'status',
            'photo_main', 'photo_interior', 'insurance_expiry',
            'technical_inspection_expiry', 'last_maintenance_date',
            'next_maintenance_date', 'maintenance_notes'
        ]


class VehicleListSerializer(serializers.ModelSerializer):
    """Serializer minimaliste pour liste de véhicules"""
    
    vehicle_type_display = serializers.CharField(source='get_vehicle_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Vehicle
        fields = [
            'id', 'registration_number', 'brand', 'model',
            'vehicle_type', 'vehicle_type_display', 'total_seats',
            'status', 'status_display', 'is_active', 'photo_main'
        ]
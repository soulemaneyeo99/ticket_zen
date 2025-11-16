"""
Serializers pour les voyages
"""
from rest_framework import serializers
from django.utils import timezone
from apps.trips.models import Trip, City
from apps.fleet.serializers import VehicleListSerializer
from apps.companies.serializers import CompanyListSerializer


class CitySerializer(serializers.ModelSerializer):
    """Serializer pour les villes"""
    
    class Meta:
        model = City
        fields = ['id', 'name', 'slug', 'country', 'latitude', 'longitude', 'is_active']
        read_only_fields = ['id', 'slug']


class TripCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un voyage"""
    
    class Meta:
        model = Trip
        fields = [
            'vehicle', 'departure_city', 'arrival_city',
            'departure_location', 'arrival_location',
            'departure_datetime', 'estimated_arrival_datetime',
            'estimated_duration', 'distance_km', 'base_price',
            'allows_cancellation', 'cancellation_deadline_hours',
            'notes', 'driver_notes'
        ]
    
    def validate(self, attrs):
        """Validations croisées"""
        # Vérifier que la ville de départ != ville d'arrivée
        if attrs['departure_city'] == attrs['arrival_city']:
            raise serializers.ValidationError({
                'arrival_city': 'La ville d\'arrivée doit être différente de la ville de départ.'
            })
        
        # Vérifier que la date de départ est dans le futur
        if attrs['departure_datetime'] <= timezone.now():
            raise serializers.ValidationError({
                'departure_datetime': 'La date de départ doit être dans le futur.'
            })
        
        # Vérifier que l'arrivée est après le départ
        if attrs['estimated_arrival_datetime'] <= attrs['departure_datetime']:
            raise serializers.ValidationError({
                'estimated_arrival_datetime': 'L\'heure d\'arrivée doit être après l\'heure de départ.'
            })
        
        # Vérifier que le véhicule appartient à la compagnie
        request = self.context.get('request')
        if request and request.user.company:
            if attrs['vehicle'].company != request.user.company:
                raise serializers.ValidationError({
                    'vehicle': 'Ce véhicule n\'appartient pas à votre compagnie.'
                })
        
        # Vérifier disponibilité du véhicule
        if not attrs['vehicle'].is_available:
            raise serializers.ValidationError({
                'vehicle': 'Ce véhicule n\'est pas disponible.'
            })
        
        return attrs
    
    def create(self, validated_data):
        """Créer un voyage"""
        request = self.context.get('request')
        
        # Ajouter la compagnie et le créateur
        validated_data['company'] = request.user.company
        validated_data['created_by'] = request.user
        
        trip = Trip.objects.create(**validated_data)
        return trip


class TripDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour un voyage"""
    
    company = CompanyListSerializer(read_only=True)
    vehicle = VehicleListSerializer(read_only=True)
    departure_city_details = CitySerializer(source='departure_city', read_only=True)
    arrival_city_details = CitySerializer(source='arrival_city', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    is_past = serializers.BooleanField(read_only=True)
    can_be_booked = serializers.BooleanField(read_only=True)
    occupancy_rate = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Trip
        fields = [
            'id', 'company', 'vehicle', 'departure_city',
            'departure_city_details', 'arrival_city', 'arrival_city_details',
            'departure_location', 'arrival_location', 'departure_datetime',
            'estimated_arrival_datetime', 'actual_departure_datetime',
            'actual_arrival_datetime', 'estimated_duration', 'distance_km',
            'base_price', 'total_seats', 'available_seats', 'reserved_seats',
            'status', 'status_display', 'is_active', 'is_recurring',
            'allows_cancellation', 'cancellation_deadline_hours',
            'notes', 'driver_notes', 'total_revenue', 'commission_amount',
            'is_full', 'is_past', 'can_be_booked', 'occupancy_rate',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'company', 'total_seats', 'available_seats',
            'reserved_seats', 'total_revenue', 'commission_amount',
            'is_full', 'is_past', 'can_be_booked', 'occupancy_rate',
            'status_display', 'created_at', 'updated_at'
        ]


class TripUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour mettre à jour un voyage"""
    
    class Meta:
        model = Trip
        fields = [
            'departure_location', 'arrival_location',
            'departure_datetime', 'estimated_arrival_datetime',
            'base_price', 'allows_cancellation',
            'cancellation_deadline_hours', 'notes', 'driver_notes',
            'status'
        ]
    
    def validate_departure_datetime(self, value):
        """Vérifier que la date de départ est dans le futur"""
        if value <= timezone.now():
            raise serializers.ValidationError('La date de départ doit être dans le futur.')
        return value


class TripListSerializer(serializers.ModelSerializer):
    """Serializer minimaliste pour liste de voyages"""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    departure_city_name = serializers.CharField(source='departure_city.name', read_only=True)
    arrival_city_name = serializers.CharField(source='arrival_city.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    occupancy_rate = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Trip
        fields = [
            'id', 'company_name', 'departure_city', 'departure_city_name',
            'arrival_city', 'arrival_city_name', 'departure_datetime',
            'base_price', 'available_seats', 'total_seats',
            'status', 'status_display', 'occupancy_rate'
        ]


class TripSearchSerializer(serializers.Serializer):
    """Serializer pour la recherche de voyages"""
    
    departure_city = serializers.IntegerField(required=True)
    arrival_city = serializers.IntegerField(required=True)
    departure_date = serializers.DateField(required=True)
    passengers = serializers.IntegerField(required=False, default=1, min_value=1, max_value=10)
    
    def validate_departure_date(self, value):
        """Vérifier que la date est dans le futur"""
        if value < timezone.now().date():
            raise serializers.ValidationError('La date de départ doit être dans le futur.')
        return value
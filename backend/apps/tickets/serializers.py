"""
Serializers pour les tickets
"""
from rest_framework import serializers
from django.utils import timezone
from apps.tickets.models import Ticket
from apps.trips.serializers import TripListSerializer
from apps.payments.serializers import PaymentDetailSerializer


class TicketCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un ticket (réservation)"""
    
    class Meta:
        model = Ticket
        fields = [
            'trip', 'passenger_first_name', 'passenger_last_name',
            'passenger_phone', 'passenger_email', 'passenger_id_number',
            'seat_number'
        ]
    
    def validate_trip(self, value):
        """Valider que le voyage peut être réservé"""
        if not value.can_be_booked:
            raise serializers.ValidationError('Ce voyage ne peut pas être réservé.')
        return value
    
    def validate_seat_number(self, value):
        """Valider la disponibilité du siège"""
        trip = self.initial_data.get('trip')
        if trip:
            # Vérifier si le siège est déjà réservé
            if Ticket.objects.filter(
                trip_id=trip,
                seat_number=value,
                status__in=[Ticket.PENDING, Ticket.CONFIRMED]
            ).exists():
                raise serializers.ValidationError('Ce siège est déjà réservé.')
        return value
    
    def validate(self, attrs):
        """Validations croisées"""
        # Vérifier qu'il reste des places
        if attrs['trip'].available_seats == 0:
            raise serializers.ValidationError({
                'trip': 'Il n\'y a plus de places disponibles pour ce voyage.'
            })
        
        return attrs
    
    def create(self, validated_data):
        """Créer un ticket"""
        request = self.context.get('request')
        
        # Ajouter le passager
        validated_data['passenger'] = request.user
        validated_data['price'] = validated_data['trip'].base_price
        
        # Calculer les frais plateforme (déjà fait dans le modèle)
        from apps.core.models import PlatformSettings
        settings = PlatformSettings.load()
        validated_data['platform_fee'] = (
            validated_data['price'] * settings.default_commission_rate / 100
        )
        
        ticket = Ticket.objects.create(**validated_data)
        return ticket


class TicketDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour un ticket"""
    
    trip = TripListSerializer(read_only=True)
    payment = PaymentDetailSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_valid = serializers.BooleanField(read_only=True)
    can_be_cancelled = serializers.BooleanField(read_only=True)
    passenger_full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_number', 'trip', 'passenger', 'passenger_first_name',
            'passenger_last_name', 'passenger_full_name', 'passenger_phone',
            'passenger_email', 'passenger_id_number', 'seat_number',
            'price', 'platform_fee', 'total_amount', 'status',
            'status_display', 'payment', 'is_paid', 'qr_code',
            'qr_code_image', 'boarding_time', 'boarded_by',
            'cancelled_at', 'cancellation_reason', 'refund_amount',
            'notes', 'is_valid', 'can_be_cancelled', 'created_at',
            'updated_at', 'confirmed_at'
        ]
        read_only_fields = [
            'id', 'ticket_number', 'total_amount', 'status_display',
            'is_valid', 'can_be_cancelled', 'passenger_full_name',
            'qr_code', 'qr_code_image', 'created_at', 'updated_at',
            'confirmed_at'
        ]


class TicketListSerializer(serializers.ModelSerializer):
    """Serializer minimaliste pour liste de tickets"""
    
    departure_city = serializers.CharField(source='trip.departure_city.name', read_only=True)
    arrival_city = serializers.CharField(source='trip.arrival_city.name', read_only=True)
    departure_datetime = serializers.DateTimeField(source='trip.departure_datetime', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_number', 'departure_city', 'arrival_city',
            'departure_datetime', 'seat_number', 'total_amount',
            'status', 'status_display', 'is_paid', 'created_at'
        ]


class TicketCancellationSerializer(serializers.Serializer):
    """Serializer pour annuler un ticket"""
    
    cancellation_reason = serializers.CharField(required=True, max_length=500)
    
    def validate(self, attrs):
        """Valider que le ticket peut être annulé"""
        ticket = self.context.get('ticket')
        
        if not ticket.can_be_cancelled:
            raise serializers.ValidationError('Ce ticket ne peut pas être annulé.')
        
        return attrs


class TicketVerificationSerializer(serializers.Serializer):
    """Serializer pour vérifier un QR code"""
    
    qr_code_data = serializers.CharField(required=True)
    trip_id = serializers.UUIDField(required=False)
    latitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False
    )
    longitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False
    )
    device_info = serializers.JSONField(required=False)
    is_offline = serializers.BooleanField(default=False)
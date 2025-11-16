"""
Serializers pour l'embarquement
"""
from rest_framework import serializers
from apps.boarding.models import BoardingPass
from apps.tickets.serializers import TicketDetailSerializer


class BoardingPassCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un boarding pass (scan QR)"""
    
    qr_code_data = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = BoardingPass
        fields = [
            'qr_code_data', 'latitude', 'longitude',
            'device_info', 'is_offline_scan', 'notes'
        ]
    
    def validate_qr_code_data(self, value):
        """Valider et décoder le QR code"""
        from utils.qr_generator import QRCodeGenerator
        
        qr_generator = QRCodeGenerator()
        
        try:
            decoded_data = qr_generator.decode_qr_code(value)
            self.context['decoded_qr'] = decoded_data
            return value
        except Exception as e:
            raise serializers.ValidationError(f'QR code invalide : {str(e)}')
    
    def create(self, validated_data):
        """Créer un boarding pass"""
        from apps.tickets.models import Ticket
        from django.utils import timezone
        
        # Retirer qr_code_data qui n'est pas un champ du modèle
        validated_data.pop('qr_code_data')
        
        # Récupérer les données décodées du QR
        decoded_data = self.context.get('decoded_qr')
        
        # Récupérer le ticket
        try:
            ticket = Ticket.objects.get(id=decoded_data['ticket_id'])
        except Ticket.DoesNotExist:
            raise serializers.ValidationError('Ticket introuvable.')
        
        # Vérifier la validité du ticket
        scan_status = BoardingPass.VALID
        
        if ticket.status == Ticket.USED:
            scan_status = BoardingPass.ALREADY_USED
        elif ticket.status != Ticket.CONFIRMED:
            scan_status = BoardingPass.INVALID
        elif str(ticket.trip.id) != decoded_data.get('trip_id'):
            scan_status = BoardingPass.WRONG_TRIP
        elif ticket.trip.departure_datetime < timezone.now() - timezone.timedelta(hours=24):
            scan_status = BoardingPass.EXPIRED
        
        # Créer le boarding pass
        boarding_pass = BoardingPass.objects.create(
            ticket=ticket,
            trip=ticket.trip,
            boarding_agent=self.context['request'].user,
            scan_status=scan_status,
            **validated_data
        )
        
        # Si scan valide, marquer le ticket comme utilisé
        if scan_status == BoardingPass.VALID:
            ticket.status = Ticket.USED
            ticket.boarding_time = timezone.now()
            ticket.boarded_by = self.context['request'].user
            ticket.save()
        
        return boarding_pass


class BoardingPassDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour un boarding pass"""
    
    ticket = TicketDetailSerializer(read_only=True)
    scan_status_display = serializers.CharField(source='get_scan_status_display', read_only=True)
    boarding_agent_name = serializers.CharField(source='boarding_agent.get_full_name', read_only=True)
    is_valid_scan = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = BoardingPass
        fields = [
            'id', 'ticket', 'trip', 'boarding_agent', 'boarding_agent_name',
            'scan_status', 'scan_status_display', 'is_valid_scan',
            'scanned_at', 'latitude', 'longitude', 'device_info',
            'is_offline_scan', 'synced_at', 'notes'
        ]
        read_only_fields = [
            'id', 'scan_status_display', 'is_valid_scan',
            'scanned_at', 'synced_at'
        ]


class BoardingPassListSerializer(serializers.ModelSerializer):
    """Serializer minimaliste pour liste de boarding passes"""
    
    ticket_number = serializers.CharField(source='ticket.ticket_number', read_only=True)
    passenger_name = serializers.CharField(source='ticket.passenger_full_name', read_only=True)
    scan_status_display = serializers.CharField(source='get_scan_status_display', read_only=True)
    
    class Meta:
        model = BoardingPass
        fields = [
            'id', 'ticket_number', 'passenger_name', 'scan_status',
            'scan_status_display', 'scanned_at', 'is_offline_scan'
        ]


class OfflineBoardingSyncSerializer(serializers.Serializer):
    """Serializer pour synchroniser les scans offline"""
    
    boarding_passes = serializers.ListField(
        child=serializers.JSONField(),
        required=True,
        allow_empty=False
    )
    
    def validate_boarding_passes(self, value):
        """Valider la structure des boarding passes"""
        required_fields = ['qr_code_data', 'scanned_at']
        
        for bp in value:
            for field in required_fields:
                if field not in bp:
                    raise serializers.ValidationError(
                        f'Champ requis manquant : {field}'
                    )
        
        return value
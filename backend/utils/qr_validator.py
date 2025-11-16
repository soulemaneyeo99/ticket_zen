"""
Service de validation de QR codes avec cache et protection anti-fraude
"""
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from apps.logs.models import ActivityLog
from utils.qr_generator import QRCodeGenerator


class QRCodeValidator:
    """Service avancé de validation de QR codes"""
    
    def __init__(self):
        self.generator = QRCodeGenerator()
    
    def validate_and_track(self, token, ticket, boarding_agent, device_info=None):
        """
        Valider un QR code et tracker l'utilisation
        
        Args:
            token: JWT token
            ticket: Instance Ticket
            boarding_agent: Utilisateur qui scanne
            device_info: Informations sur l'appareil
        
        Returns:
            dict: Résultat de la validation avec détails
        """
        # Clé de cache pour éviter les scans multiples rapides
        cache_key = f'qr_scan_{ticket.id}_{boarding_agent.id}'
        
        # Vérifier si un scan récent existe (protection contre double scan)
        recent_scan = cache.get(cache_key)
        if recent_scan:
            return {
                'is_valid': False,
                'error_code': 'RECENT_SCAN',
                'error_message': 'Ce ticket a été scanné il y a moins de 5 minutes',
                'last_scan_time': recent_scan
            }
        
        # Valider le QR code
        validation_result = self.generator.verify_ticket_qr(token, ticket)
        
        if not validation_result['is_valid']:
            # Logger la tentative invalide
            ActivityLog.objects.create(
                user=boarding_agent,
                action=ActivityLog.TICKET_SCAN,
                description=f"Scan QR invalide : {ticket.ticket_number}",
                details={
                    'ticket_id': str(ticket.id),
                    'ticket_number': ticket.ticket_number,
                    'error': validation_result['error_message'],
                    'device_info': device_info
                },
                severity=ActivityLog.SEVERITY_WARNING
            )
            
            # Incrémenter le compteur de tentatives invalides
            self._increment_invalid_attempts(ticket)
            
            return {
                'is_valid': False,
                'error_code': 'INVALID_QR',
                'error_message': validation_result['error_message']
            }
        
        # Mettre en cache le scan pendant 5 minutes
        cache.set(cache_key, timezone.now().isoformat(), 300)
        
        # Logger le scan valide
        ActivityLog.objects.create(
            user=boarding_agent,
            action=ActivityLog.TICKET_SCAN,
            description=f"Scan QR valide : {ticket.ticket_number}",
            details={
                'ticket_id': str(ticket.id),
                'ticket_number': ticket.ticket_number,
                'trip_id': str(ticket.trip.id),
                'passenger': ticket.passenger_full_name,
                'seat': ticket.seat_number,
                'device_info': device_info,
                'decoded_data': validation_result['decoded_data']
            },
            severity=ActivityLog.SEVERITY_INFO
        )
        
        return {
            'is_valid': True,
            'error_code': None,
            'error_message': None,
            'decoded_data': validation_result['decoded_data']
        }
    
    def _increment_invalid_attempts(self, ticket):
        """Incrémenter le compteur de tentatives invalides"""
        cache_key = f'invalid_attempts_{ticket.id}'
        attempts = cache.get(cache_key, 0)
        attempts += 1
        
        # Garder en cache pendant 1 heure
        cache.set(cache_key, attempts, 3600)
        
        # Alerter si trop de tentatives (possible fraude)
        if attempts >= 5:
            ActivityLog.objects.create(
                action=ActivityLog.TICKET_SCAN,
                description=f"ALERTE FRAUDE : Nombreuses tentatives de scan invalides pour ticket {ticket.ticket_number}",
                details={
                    'ticket_id': str(ticket.id),
                    'ticket_number': ticket.ticket_number,
                    'invalid_attempts': attempts
                },
                severity=ActivityLog.SEVERITY_CRITICAL
            )
    
    def check_fraud_patterns(self, ticket):
        """
        Vérifier les patterns de fraude pour un ticket
        
        Returns:
            dict: Résultat de l'analyse anti-fraude
        """
        fraud_indicators = []
        risk_level = 'low'
        
        # Vérifier le nombre de tentatives invalides
        cache_key = f'invalid_attempts_{ticket.id}'
        invalid_attempts = cache.get(cache_key, 0)
        
        if invalid_attempts >= 3:
            fraud_indicators.append({
                'type': 'multiple_invalid_attempts',
                'count': invalid_attempts,
                'severity': 'high' if invalid_attempts >= 5 else 'medium'
            })
            risk_level = 'high' if invalid_attempts >= 5 else 'medium'
        
        # Vérifier si le ticket a été utilisé plusieurs fois
        from apps.boarding.models import BoardingPass
        boarding_passes = BoardingPass.objects.filter(ticket=ticket)
        
        if boarding_passes.count() > 1:
            fraud_indicators.append({
                'type': 'multiple_boardings',
                'count': boarding_passes.count(),
                'severity': 'critical'
            })
            risk_level = 'critical'
        
        # Vérifier si le QR a été scanné de plusieurs endroits différents
        unique_agents = boarding_passes.values('boarding_agent').distinct().count()
        if unique_agents > 2:
            fraud_indicators.append({
                'type': 'multiple_agents',
                'count': unique_agents,
                'severity': 'high'
            })
            risk_level = 'high'
        
        return {
            'ticket_id': str(ticket.id),
            'ticket_number': ticket.ticket_number,
            'risk_level': risk_level,
            'fraud_indicators': fraud_indicators,
            'requires_investigation': risk_level in ['high', 'critical']
        }
    
    def validate_bulk_qr_codes(self, qr_data_list, trip_id):
        """
        Valider plusieurs QR codes en batch (mode offline sync)
        
        Args:
            qr_data_list: Liste de tokens JWT
            trip_id: ID du voyage
        
        Returns:
            dict: Résultats de validation groupés
        """
        results = {
            'valid': [],
            'invalid': [],
            'total': len(qr_data_list)
        }
        
        for qr_data in qr_data_list:
            try:
                validation = self.generator.validate_offline_qr(
                    qr_data['token'],
                    trip_id
                )
                
                if validation['is_valid']:
                    results['valid'].append({
                        'token': qr_data['token'],
                        'decoded_data': validation['decoded_data']
                    })
                else:
                    results['invalid'].append({
                        'token': qr_data['token'],
                        'error': validation['error_message']
                    })
            
            except Exception as e:
                results['invalid'].append({
                    'token': qr_data.get('token', 'unknown'),
                    'error': str(e)
                })
        
        return results


class OfflineQRValidator:
    """Validateur QR pour mode hors ligne"""
    
    def __init__(self):
        self.generator = QRCodeGenerator()
    
    def validate_offline(self, token, trip_data):
        """
        Valider un QR code en mode offline avec données du voyage en cache
        
        Args:
            token: JWT token
            trip_data: Données du voyage (préchargées)
        
        Returns:
            dict: Résultat de validation
        """
        try:
            # Décoder le token
            decoded = self.generator.decode_qr_code(token)
            
            # Vérifier la correspondance avec le voyage
            if str(trip_data['id']) != decoded.get('trip_id'):
                return {
                    'is_valid': False,
                    'error': 'QR code ne correspond pas à ce voyage',
                    'needs_sync': False
                }
            
            # Vérifier l'expiration
            if decoded.get('exp') and timezone.now().timestamp() > decoded['exp']:
                return {
                    'is_valid': False,
                    'error': 'QR code expiré',
                    'needs_sync': False
                }
            
            # Vérifier dans le cache local si le ticket n'a pas déjà été scanné
            cache_key = f'offline_scanned_{decoded["ticket_id"]}'
            if cache.get(cache_key):
                return {
                    'is_valid': False,
                    'error': 'Ce ticket a déjà été scanné (cache local)',
                    'needs_sync': True
                }
            
            # Marquer comme scanné localement
            cache.set(cache_key, True, 86400)  # 24 heures
            
            return {
                'is_valid': True,
                'error': None,
                'decoded_data': decoded,
                'needs_sync': True  # Doit être synchronisé avec le serveur
            }
        
        except Exception as e:
            return {
                'is_valid': False,
                'error': str(e),
                'needs_sync': False
            }
    
    def prepare_offline_data(self, trip):
        """
        Préparer les données pour validation offline
        
        Args:
            trip: Instance Trip
        
        Returns:
            dict: Données à stocker localement
        """
        from apps.tickets.models import Ticket
        
        # Récupérer tous les tickets confirmés du voyage
        tickets = Ticket.objects.filter(
            trip=trip,
            status__in=[Ticket.CONFIRMED, Ticket.PENDING]
        ).select_related('passenger')
        
        return {
            'trip_id': str(trip.id),
            'departure_city': trip.departure_city.name,
            'arrival_city': trip.arrival_city.name,
            'departure_datetime': trip.departure_datetime.isoformat(),
            'total_seats': trip.total_seats,
            'tickets': [
                {
                    'ticket_id': str(ticket.id),
                    'ticket_number': ticket.ticket_number,
                    'passenger_name': ticket.passenger_full_name,
                    'seat_number': ticket.seat_number,
                    'status': ticket.status
                }
                for ticket in tickets
            ],
            'synced_at': timezone.now().isoformat()
        }
"""
Générateur de QR codes sécurisés avec JWT RS256
"""
import jwt
import qrcode
import io
import base64
from datetime import datetime, timedelta
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import os


class QRCodeGenerator:
    """Classe pour générer et valider des QR codes sécurisés"""
    
    def __init__(self):
        """Initialiser le générateur avec les clés RSA"""
        self.private_key_path = settings.QR_CODE_RSA_PRIVATE_KEY_PATH
        self.public_key_path = settings.QR_CODE_RSA_PUBLIC_KEY_PATH
        
        # Créer les clés si elles n'existent pas
        if not os.path.exists(self.private_key_path) or not os.path.exists(self.public_key_path):
            self._generate_rsa_keys()
        
        # Charger les clés
        self.private_key = self._load_private_key()
        self.public_key = self._load_public_key()
    
    def _generate_rsa_keys(self):
        """Générer une paire de clés RSA"""
        # Créer le dossier keys s'il n'existe pas
        os.makedirs(os.path.dirname(self.private_key_path), exist_ok=True)
        
        # Générer la clé privée
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # Sauvegarder la clé privée
        with open(self.private_key_path, 'wb') as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Extraire et sauvegarder la clé publique
        public_key = private_key.public_key()
        with open(self.public_key_path, 'wb') as f:
            f.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))
        
        print(f"✅ Clés RSA générées avec succès:")
        print(f"   - Clé privée: {self.private_key_path}")
        print(f"   - Clé publique: {self.public_key_path}")
    
    def _load_private_key(self):
        """Charger la clé privée"""
        with open(self.private_key_path, 'rb') as f:
            return serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend()
            )
    
    def _load_public_key(self):
        """Charger la clé publique"""
        with open(self.public_key_path, 'rb') as f:
            return serialization.load_pem_public_key(
                f.read(),
                backend=default_backend()
            )
    
    def generate_qr_code(self, ticket):
        """
        Générer un QR code sécurisé pour un ticket
        
        Args:
            ticket: Instance du modèle Ticket
        
        Returns:
            dict: {
                'token': JWT token signé,
                'image': Fichier image du QR code,
                'image_base64': Image encodée en base64
            }
        """
        # Créer le payload JWT
        expiration_hours = getattr(settings, 'QR_CODE_EXPIRATION_HOURS', 24)
        expiration_date = ticket.trip.departure_datetime + timedelta(hours=expiration_hours)
        
        payload = {
            'ticket_id': str(ticket.id),
            'ticket_number': ticket.ticket_number,
            'trip_id': str(ticket.trip.id),
            'passenger_name': ticket.passenger_full_name,
            'seat_number': ticket.seat_number,
            'departure_datetime': ticket.trip.departure_datetime.isoformat(),
            'departure_city': ticket.trip.departure_city.name,
            'arrival_city': ticket.trip.arrival_city.name,
            'issued_at': timezone.now().isoformat(),
            'exp': int(expiration_date.timestamp()),
            'iss': 'TicketZen',
            'type': 'ticket_qr'
        }
        
        # Signer le token avec RS256
        token = jwt.encode(
            payload,
            self.private_key,
            algorithm='RS256'
        )
        
        # Générer l'image QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        
        qr.add_data(token)
        qr.make(fit=True)
        
        # Créer l'image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Sauvegarder dans un buffer
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Encoder en base64 pour l'affichage
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Créer un fichier Django
        buffer.seek(0)
        image_file = ContentFile(buffer.read(), name=f'qr_{ticket.ticket_number}.png')
        
        return {
            'token': token,
            'image': image_file,
            'image_base64': image_base64
        }
    
    def decode_qr_code(self, token):
        """
        Décoder et valider un QR code
        
        Args:
            token: JWT token à décoder
        
        Returns:
            dict: Payload décodé
        
        Raises:
            jwt.ExpiredSignatureError: Si le token a expiré
            jwt.InvalidTokenError: Si le token est invalide
        """
        try:
            # Décoder le token avec la clé publique
            payload = jwt.decode(
                token,
                self.public_key,
                algorithms=['RS256'],
                options={
                    'verify_signature': True,
                    'verify_exp': True,
                    'verify_iss': True
                },
                issuer='TicketZen'
            )
            
            # Vérifier le type
            if payload.get('type') != 'ticket_qr':
                raise jwt.InvalidTokenError('Type de token invalide')
            
            return payload
        
        except jwt.ExpiredSignatureError:
            raise Exception('QR code expiré')
        
        except jwt.InvalidSignatureError:
            raise Exception('Signature QR code invalide - possible fraude')
        
        except jwt.InvalidTokenError as e:
            raise Exception(f'QR code invalide : {str(e)}')
    
    def verify_ticket_qr(self, token, ticket):
        """
        Vérifier qu'un QR code correspond à un ticket
        
        Args:
            token: JWT token à vérifier
            ticket: Instance du modèle Ticket
        
        Returns:
            dict: {
                'is_valid': bool,
                'error_message': str ou None,
                'decoded_data': dict ou None
            }
        """
        try:
            # Décoder le token
            decoded_data = self.decode_qr_code(token)
            
            # Vérifier la correspondance avec le ticket
            if str(ticket.id) != decoded_data.get('ticket_id'):
                return {
                    'is_valid': False,
                    'error_message': 'QR code ne correspond pas au ticket',
                    'decoded_data': decoded_data
                }
            
            if ticket.ticket_number != decoded_data.get('ticket_number'):
                return {
                    'is_valid': False,
                    'error_message': 'Numéro de ticket invalide',
                    'decoded_data': decoded_data
                }
            
            # Vérifier que le ticket n'a pas déjà été utilisé
            if ticket.status == 'used':
                return {
                    'is_valid': False,
                    'error_message': 'Ce ticket a déjà été utilisé',
                    'decoded_data': decoded_data
                }
            
            # Vérifier que le ticket est confirmé
            if ticket.status != 'confirmed':
                return {
                    'is_valid': False,
                    'error_message': 'Ticket non confirmé',
                    'decoded_data': decoded_data
                }
            
            return {
                'is_valid': True,
                'error_message': None,
                'decoded_data': decoded_data
            }
        
        except Exception as e:
            return {
                'is_valid': False,
                'error_message': str(e),
                'decoded_data': None
            }
    
    def regenerate_qr_code(self, ticket):
        """
        Régénérer un QR code pour un ticket (réémission)
        
        Args:
            ticket: Instance du modèle Ticket
        
        Returns:
            dict: Nouveau QR code
        """
        # Supprimer l'ancien QR code si existant
        if ticket.qr_code_image:
            ticket.qr_code_image.delete(save=False)
        
        # Générer un nouveau QR code
        return self.generate_qr_code(ticket)
    
    def validate_offline_qr(self, token, trip_id, current_datetime=None):
        """
        Valider un QR code en mode hors ligne
        (vérifications basiques sans accès à la base de données)
        
        Args:
            token: JWT token
            trip_id: ID du voyage
            current_datetime: Date/heure actuelle (pour tests)
        
        Returns:
            dict: Résultat de la validation
        """
        if current_datetime is None:
            current_datetime = timezone.now()
        
        try:
            # Décoder le token
            decoded_data = self.decode_qr_code(token)
            
            # Vérifier que le trip_id correspond
            if str(trip_id) != decoded_data.get('trip_id'):
                return {
                    'is_valid': False,
                    'error_message': 'QR code ne correspond pas à ce voyage',
                    'decoded_data': decoded_data
                }
            
            # Vérifier l'expiration
            exp_timestamp = decoded_data.get('exp')
            if exp_timestamp and current_datetime.timestamp() > exp_timestamp:
                return {
                    'is_valid': False,
                    'error_message': 'QR code expiré',
                    'decoded_data': decoded_data
                }
            
            return {
                'is_valid': True,
                'error_message': None,
                'decoded_data': decoded_data
            }
        
        except Exception as e:
            return {
                'is_valid': False,
                'error_message': str(e),
                'decoded_data': None
            }
    
    @staticmethod
    def generate_test_token():
        """Générer un token de test pour le développement"""
        generator = QRCodeGenerator()
        
        # Payload de test
        payload = {
            'ticket_id': 'test-12345',
            'ticket_number': 'TZ20250101123456',
            'trip_id': 'test-trip-67890',
            'passenger_name': 'Test User',
            'seat_number': 'A1',
            'departure_datetime': timezone.now().isoformat(),
            'departure_city': 'Abidjan',
            'arrival_city': 'Yamoussoukro',
            'issued_at': timezone.now().isoformat(),
            'exp': int((timezone.now() + timedelta(days=1)).timestamp()),
            'iss': 'TicketZen',
            'type': 'ticket_qr'
        }
        
        token = jwt.encode(
            payload,
            generator.private_key,
            algorithm='RS256'
        )
        
        return token


# Fonction helper pour générer les clés au démarrage
def ensure_rsa_keys_exist():
    """S'assurer que les clés RSA existent"""
    generator = QRCodeGenerator()
    return {
        'private_key_path': generator.private_key_path,
        'public_key_path': generator.public_key_path
    }
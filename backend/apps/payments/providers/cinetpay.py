"""
Provider CinetPay (mocké pour le développement)
"""
import requests
import hashlib
import json
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from django.db import transaction

from apps.payments.providers.base import BasePaymentProvider
from apps.payments.models import Payment
from apps.tickets.models import Ticket
from apps.logs.models import ActivityLog


class CinetPayProvider(BasePaymentProvider):
    """Provider pour CinetPay (mode mocké)"""
    
    def __init__(self):
        super().__init__()
        self.api_key = getattr(settings, 'CINETPAY_API_KEY', '')
        self.site_id = getattr(settings, 'CINETPAY_SITE_ID', '')
        self.secret_key = getattr(settings, 'CINETPAY_SECRET_KEY', '')
        self.mode = getattr(settings, 'CINETPAY_MODE', 'TEST')
        
        # URLs CinetPay
        if self.mode == 'PRODUCTION':
            self.base_url = 'https://api-checkout.cinetpay.com/v2'
        else:
            self.base_url = 'https://api-checkout.cinetpay.com/v2'  # Même URL en test
        
        self.is_mocked = True  # Activer le mode mocké
    
    def initialize_payment(self, payment, ticket, return_url='', notify_url=''):
        """
        Initialiser un paiement CinetPay
        
        En mode mocké, on simule la réponse de CinetPay
        """
        try:
            # Préparer les données
            payment_data = {
                'apikey': self.api_key,
                'site_id': self.site_id,
                'transaction_id': payment.transaction_id,
                'amount': int(payment.amount),  # Montant en FCFA (entier)
                'currency': 'XOF',
                'alternative_currency': '',
                'description': f'Paiement ticket {ticket.ticket_number}',
                'customer_id': str(ticket.passenger.id),
                'customer_name': ticket.passenger_full_name,
                'customer_surname': ticket.passenger_last_name,
                'customer_email': ticket.passenger_email,
                'customer_phone_number': ticket.passenger_phone,
                'customer_address': '',
                'customer_city': '',
                'customer_country': 'CI',
                'customer_state': '',
                'customer_zip_code': '',
                'notify_url': notify_url or settings.CINETPAY_NOTIFY_URL,
                'return_url': return_url or f'{settings.CORS_ALLOWED_ORIGINS[0]}/payment-success',
                'channels': 'ALL',  # Tous les moyens de paiement
                'metadata': json.dumps({
                    'ticket_id': str(ticket.id),
                    'trip_id': str(ticket.trip.id),
                    'company_id': str(ticket.trip.company.id)
                }),
                'lang': 'fr'
            }
            
            # MODE MOCKÉ - Simuler la réponse CinetPay
            if self.is_mocked:
                return self._mock_initialize_payment(payment_data, payment)
            
            # MODE RÉEL - Appel API CinetPay
            response = requests.post(
                f'{self.base_url}/payment',
                json=payment_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get('code') == '201':
                # Succès
                self.log_transaction('init', {
                    'payment_id': str(payment.id),
                    'transaction_id': payment.transaction_id,
                    'amount': str(payment.amount),
                    'response': response_data
                })
                
                return {
                    'success': True,
                    'transaction_id': response_data['data']['payment_token'],
                    'payment_url': response_data['data']['payment_url'],
                    'message': 'Paiement initialisé avec succès'
                }
            else:
                # Erreur
                return {
                    'success': False,
                    'transaction_id': '',
                    'payment_url': '',
                    'message': response_data.get('message', 'Erreur lors de l\'initialisation du paiement')
                }
        
        except Exception as e:
            return {
                'success': False,
                'transaction_id': '',
                'payment_url': '',
                'message': f'Erreur : {str(e)}'
            }
    
    def _mock_initialize_payment(self, payment_data, payment):
        """
        Simuler l'initialisation d'un paiement (mode développement)
        """
        import uuid
        
        # Générer un token de paiement mocké
        payment_token = f"MOCK_{uuid.uuid4().hex[:16].upper()}"
        
        # URL de paiement mockée (redirige vers une page de test)
        payment_url = f"{settings.CORS_ALLOWED_ORIGINS[0]}/mock-payment/{payment_token}"
        
        # Logger
        self.log_transaction('init_mock', {
            'payment_id': str(payment.id),
            'transaction_id': payment.transaction_id,
            'amount': payment_data['amount'],
            'payment_token': payment_token,
            'mode': 'MOCKED'
        })
        
        return {
            'success': True,
            'transaction_id': payment_token,
            'payment_url': payment_url,
            'message': 'Paiement initialisé (MODE MOCKÉ)',
            'is_mock': True
        }
    
    def check_payment_status(self, transaction_id):
        """
        Vérifier le statut d'un paiement
        """
        try:
            # MODE MOCKÉ
            if self.is_mocked or transaction_id.startswith('MOCK_'):
                return self._mock_check_status(transaction_id)
            
            # MODE RÉEL
            check_data = {
                'apikey': self.api_key,
                'site_id': self.site_id,
                'transaction_id': transaction_id
            }
            
            response = requests.post(
                f'{self.base_url}/payment/check',
                json=check_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get('code') == '00':
                data = response_data.get('data', {})
                
                # Mapper le statut CinetPay
                status_map = {
                    'ACCEPTED': Payment.SUCCESS,
                    'PENDING': Payment.PROCESSING,
                    'REFUSED': Payment.FAILED,
                    'CANCELLED': Payment.CANCELLED
                }
                
                return {
                    'success': True,
                    'status': status_map.get(data.get('status'), Payment.FAILED),
                    'amount': float(data.get('amount', 0)),
                    'transaction_id': transaction_id,
                    'data': data
                }
            
            return {
                'success': False,
                'status': Payment.FAILED,
                'amount': 0,
                'transaction_id': transaction_id,
                'data': response_data
            }
        
        except Exception as e:
            return {
                'success': False,
                'status': Payment.FAILED,
                'amount': 0,
                'transaction_id': transaction_id,
                'data': {'error': str(e)}
            }
    
    def _mock_check_status(self, transaction_id):
        """
        Simuler la vérification de statut (mode développement)
        """
        # En mode mock, on retourne toujours SUCCESS après quelques secondes
        return {
            'success': True,
            'status': Payment.SUCCESS,
            'amount': 0,  # Sera récupéré depuis la base
            'transaction_id': transaction_id,
            'data': {
                'status': 'ACCEPTED',
                'payment_method': 'MOCK',
                'operator_id': 'MOCK_OPERATOR',
                'payment_date': timezone.now().isoformat(),
                'is_mock': True
            }
        }
    
    @transaction.atomic
    def handle_webhook(self, webhook_data):
        """
        Traiter une notification webhook CinetPay
        """
        try:
            # Récupérer les données du webhook
            cpm_trans_id = webhook_data.get('cpm_trans_id')
            cpm_site_id = webhook_data.get('cpm_site_id')
            cpm_trans_status = webhook_data.get('cpm_trans_status')
            cpm_amount = webhook_data.get('cpm_amount')
            signature = webhook_data.get('signature', '')
            
            # Vérifier le site_id
            if cpm_site_id != self.site_id and not self.is_mocked:
                return {
                    'success': False,
                    'payment': None,
                    'message': 'Site ID invalide'
                }
            
            # Vérifier la signature (si mode réel)
            if not self.is_mocked and not self.validate_webhook_signature(webhook_data, signature):
                return {
                    'success': False,
                    'payment': None,
                    'message': 'Signature invalide'
                }
            
            # Trouver le paiement
            # Le cpm_trans_id peut être soit notre transaction_id, soit le payment_token
            payment = None
            try:
                payment = Payment.objects.select_related('trip', 'company', 'user').get(
                    transaction_id=cpm_trans_id
                )
            except Payment.DoesNotExist:
                try:
                    payment = Payment.objects.select_related('trip', 'company', 'user').get(
                        provider_transaction_id=cpm_trans_id
                    )
                except Payment.DoesNotExist:
                    return {
                        'success': False,
                        'payment': None,
                        'message': 'Paiement introuvable'
                    }
            
            # Vérifier que le paiement n'a pas déjà été traité
            if payment.status == Payment.SUCCESS:
                return {
                    'success': True,
                    'payment': payment,
                    'message': 'Paiement déjà traité'
                }
            
            # Mettre à jour le statut selon la réponse CinetPay
            if cpm_trans_status == '00':  # Succès
                payment.status = Payment.SUCCESS
                payment.completed_at = timezone.now()
                
                # Confirmer le ticket associé
                if hasattr(payment, 'ticket'):
                    ticket = payment.ticket
                    ticket.status = Ticket.CONFIRMED
                    ticket.confirmed_at = timezone.now()
                    ticket.is_paid = True
                    ticket.save()
                    
                    # Générer le QR code
                    from apps.tickets.services import TicketService
                    ticket_service = TicketService()
                    ticket_service.create_and_generate_qr(ticket)
                
            elif cpm_trans_status in ['01', '02']:  # En cours
                payment.status = Payment.PROCESSING
            
            else:  # Échec
                payment.status = Payment.FAILED
                
                # Libérer le siège si ticket existe
                if hasattr(payment, 'ticket'):
                    payment.ticket.status = Ticket.CANCELLED
                    payment.ticket.trip.release_seats(1)
                    payment.ticket.save()
            
            # Sauvegarder la réponse du provider
            payment.provider_response = webhook_data
            payment.save()
            
            # Logger
            ActivityLog.objects.create(
                user=payment.user,
                action=ActivityLog.PAYMENT_SUCCESS if payment.status == Payment.SUCCESS else ActivityLog.PAYMENT_FAILED,
                description=f"Webhook CinetPay : {payment.transaction_id} - {payment.get_status_display()}",
                details={
                    'payment_id': str(payment.id),
                    'transaction_id': payment.transaction_id,
                    'status': payment.status,
                    'amount': str(payment.amount),
                    'webhook_data': webhook_data
                },
                severity=ActivityLog.SEVERITY_INFO if payment.status == Payment.SUCCESS else ActivityLog.SEVERITY_WARNING
            )
            
            # Envoyer une notification
            from apps.notifications.models import Notification
            if payment.status == Payment.SUCCESS:
                Notification.objects.create(
                    user=payment.user,
                    notification_type=Notification.EMAIL,
                    category=Notification.PAYMENT_SUCCESS,
                    title='Paiement réussi',
                    message=f'Votre paiement de {payment.amount} FCFA a été effectué avec succès.',
                    metadata={
                        'payment_id': str(payment.id),
                        'transaction_id': payment.transaction_id
                    }
                )
            else:
                Notification.objects.create(
                    user=payment.user,
                    notification_type=Notification.EMAIL,
                    category=Notification.PAYMENT_FAILED,
                    title='Paiement échoué',
                    message=f'Votre paiement de {payment.amount} FCFA a échoué. Veuillez réessayer.',
                    metadata={
                        'payment_id': str(payment.id),
                        'transaction_id': payment.transaction_id
                    }
                )
            
            return {
                'success': True,
                'payment': payment,
                'message': 'Webhook traité avec succès'
            }
        
        except Exception as e:
            return {
                'success': False,
                'payment': None,
                'message': f'Erreur : {str(e)}'
            }
    
    def validate_webhook_signature(self, webhook_data, signature):
        """
        Valider la signature du webhook CinetPay
        """
        if self.is_mocked:
            return True
        
        # Construire la chaîne à signer selon la documentation CinetPay
        # Format: cpm_site_id + cpm_trans_id + cpm_trans_status + cpm_amount + secret_key
        signature_string = (
            f"{webhook_data.get('cpm_site_id')}"
            f"{webhook_data.get('cpm_trans_id')}"
            f"{webhook_data.get('cpm_trans_status')}"
            f"{webhook_data.get('cpm_amount')}"
            f"{self.secret_key}"
        )
        
        # Calculer le hash SHA256
        calculated_signature = hashlib.sha256(signature_string.encode()).hexdigest()
        
        return calculated_signature == signature
    
    def refund_payment(self, payment, amount):
        """
        Rembourser un paiement
        """
        try:
            # MODE MOCKÉ
            if self.is_mocked or payment.provider_transaction_id.startswith('MOCK_'):
                return self._mock_refund(payment, amount)
            
            # MODE RÉEL
            refund_data = {
                'apikey': self.api_key,
                'site_id': self.site_id,
                'transaction_id': payment.provider_transaction_id,
                'amount': int(amount)
            }
            
            response = requests.post(
                f'{self.base_url}/payment/refund',
                json=refund_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get('code') == '00':
                return {
                    'success': True,
                    'refund_transaction_id': response_data.get('data', {}).get('refund_transaction_id', ''),
                    'message': 'Remboursement effectué avec succès'
                }
            
            return {
                'success': False,
                'refund_transaction_id': '',
                'message': response_data.get('message', 'Erreur lors du remboursement')
            }
        
        except Exception as e:
            return {
                'success': False,
                'refund_transaction_id': '',
                'message': f'Erreur : {str(e)}'
            }
    
    def _mock_refund(self, payment, amount):
        """
        Simuler un remboursement (mode développement)
        """
        import uuid
        
        refund_transaction_id = f"REFUND_MOCK_{uuid.uuid4().hex[:12].upper()}"
        
        # Logger
        ActivityLog.objects.create(
            user=payment.user,
            action=ActivityLog.PAYMENT_REFUND,
            description=f"Remboursement mocké : {payment.transaction_id}",
            details={
                'payment_id': str(payment.id),
                'amount': str(amount),
                'refund_transaction_id': refund_transaction_id,
                'mode': 'MOCKED'
            },
            severity=ActivityLog.SEVERITY_INFO
        )
        
        return {
            'success': True,
            'refund_transaction_id': refund_transaction_id,
            'message': 'Remboursement effectué (MODE MOCKÉ)',
            'is_mock': True
        }
    
    def simulate_successful_payment(self, payment):
        """
        Simuler un paiement réussi (pour tests)
        Utile pour le développement
        """
        webhook_data = {
            'cpm_trans_id': payment.transaction_id,
            'cpm_site_id': self.site_id,
            'cpm_trans_status': '00',  # Succès
            'cpm_amount': str(int(payment.amount)),
            'cpm_currency': 'XOF',
            'cpm_payid': payment.provider_transaction_id or f"MOCK_PAY_{payment.transaction_id}",
            'cpm_payment_date': timezone.now().strftime('%Y-%m-%d'),
            'cpm_payment_time': timezone.now().strftime('%H:%M:%S'),
            'payment_method': 'MOCK',
            'cel_phone_num': payment.phone_number,
            'cpm_phone_prefixe': '225',
            'cpm_language': 'fr',
            'cpm_version': 'V2',
            'cpm_payment_config': 'SINGLE',
            'cpm_page_action': 'PAYMENT',
            'cpm_custom': json.dumps({
                'ticket_id': str(payment.ticket.id) if hasattr(payment, 'ticket') else '',
                'is_mock': True
            }),
            'cpm_designation': f'Paiement ticket',
            'buyer_name': payment.user.get_full_name(),
            'signature': 'MOCK_SIGNATURE',
            'is_mock': True
        }
        
        return self.handle_webhook(webhook_data)
    
    def simulate_failed_payment(self, payment):
        """
        Simuler un paiement échoué (pour tests)
        """
        webhook_data = {
            'cpm_trans_id': payment.transaction_id,
            'cpm_site_id': self.site_id,
            'cpm_trans_status': '01',  # Échec
            'cpm_amount': str(int(payment.amount)),
            'cpm_error_message': 'Paiement refusé (SIMULATION)',
            'is_mock': True
        }
        
        return self.handle_webhook(webhook_data)
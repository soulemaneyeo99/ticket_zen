"""
Services pour la gestion des paiements
"""
from django.db import transaction
from django.utils import timezone
from decimal import Decimal

from apps.payments.models import Payment
from apps.payments.providers.cinetpay import CinetPayProvider
from apps.tickets.models import Ticket
from apps.logs.models import ActivityLog


class PaymentService:
    """Service pour la gestion des paiements"""
    
    def __init__(self):
        self.provider = CinetPayProvider()
    
    @transaction.atomic
    def create_payment(self, ticket, payment_method, phone_number='', request=None):
        """
        Créer un paiement pour un ticket
        
        Args:
            ticket: Instance Ticket
            payment_method: Méthode de paiement
            phone_number: Numéro de téléphone (pour mobile money)
            request: Request Django (pour IP, user agent)
        
        Returns:
            Payment: Instance Payment créée
        """
        # Vérifier que le ticket n'est pas déjà payé
        if ticket.is_paid:
            raise ValueError('Ce ticket est déjà payé')
        
        # Calculer les montants
        from apps.core.models import PlatformSettings
        settings = PlatformSettings.load()
        
        platform_commission = ticket.trip.company.calculate_commission(ticket.total_amount)
        company_amount = ticket.total_amount - platform_commission
        
        # Créer le paiement
        payment = Payment.objects.create(
            user=ticket.passenger,
            trip=ticket.trip,
            company=ticket.trip.company,
            amount=ticket.total_amount,
            platform_commission=platform_commission,
            company_amount=company_amount,
            payment_method=payment_method,
            phone_number=phone_number,
            ip_address=self._get_client_ip(request) if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT', '') if request else ''
        )
        
        # Associer le paiement au ticket
        ticket.payment = payment
        ticket.save()
        
        return payment
    
    def initialize_payment_with_provider(self, payment, ticket, return_url='', notify_url=''):
        """
        Initialiser le paiement avec le provider (CinetPay)
        
        Args:
            payment: Instance Payment
            ticket: Instance Ticket
            return_url: URL de retour
            notify_url: URL de notification
        
        Returns:
            dict: Résultat de l'initialisation
        """
        result = self.provider.initialize_payment(
            payment=payment,
            ticket=ticket,
            return_url=return_url,
            notify_url=notify_url
        )
        
        if result['success']:
            # Mettre à jour le paiement
            payment.provider_transaction_id = result['transaction_id']
            payment.payment_url = result['payment_url']
            payment.status = Payment.PROCESSING
            payment.provider_response = result
            payment.save()
        else:
            # Marquer comme échoué
            payment.status = Payment.FAILED
            payment.provider_response = result
            payment.save()
        
        return result
    
    def check_payment_status(self, payment):
        """
        Vérifier le statut d'un paiement auprès du provider
        
        Args:
            payment: Instance Payment
        
        Returns:
            dict: Statut du paiement
        """
        if not payment.provider_transaction_id:
            return {
                'success': False,
                'status': Payment.PENDING,
                'message': 'Aucune transaction provider trouvée'
            }
        
        result = self.provider.check_payment_status(payment.provider_transaction_id)
        
        if result['success']:
            # Mettre à jour le statut si changé
            if payment.status != result['status']:
                old_status = payment.status
                payment.status = result['status']
                payment.provider_response = result['data']
                
                if result['status'] == Payment.SUCCESS:
                    payment.completed_at = timezone.now()
                
                payment.save()
                
                # Logger le changement
                ActivityLog.objects.create(
                    user=payment.user,
                    action=ActivityLog.PAYMENT_SUCCESS if result['status'] == Payment.SUCCESS else ActivityLog.PAYMENT_FAILED,
                    description=f"Changement statut paiement : {old_status} → {result['status']}",
                    details={
                        'payment_id': str(payment.id),
                        'old_status': old_status,
                        'new_status': result['status']
                    },
                    severity=ActivityLog.SEVERITY_INFO
                )
        
        return result
    
    @transaction.atomic
    def process_refund(self, payment, refund_amount, refund_reason, admin_user):
        """
        Traiter un remboursement
        
        Args:
            payment: Instance Payment
            refund_amount: Montant à rembourser
            refund_reason: Raison du remboursement
            admin_user: Utilisateur admin qui effectue le remboursement
        
        Returns:
            dict: Résultat du remboursement
        """
        # Vérifier que le paiement peut être remboursé
        if not payment.can_be_refunded:
            return {
                'success': False,
                'message': 'Ce paiement ne peut pas être remboursé'
            }
        
        # Vérifier le montant
        if refund_amount > payment.amount:
            return {
                'success': False,
                'message': 'Le montant du remboursement ne peut pas dépasser le montant du paiement'
            }
        
        # Initier le remboursement avec le provider
        result = self.provider.refund_payment(payment, refund_amount)
        
        if result['success']:
            # Mettre à jour le paiement
            payment.status = Payment.REFUNDED
            payment.refund_amount = refund_amount
            payment.refund_reason = refund_reason
            payment.refunded_at = timezone.now()
            payment.refund_transaction_id = result['refund_transaction_id']
            payment.save()
            
            # Mettre à jour le ticket
            if hasattr(payment, 'ticket'):
                ticket = payment.ticket
                ticket.status = Ticket.REFUNDED
                ticket.refund_amount = refund_amount
                ticket.save()
                
                # Libérer le siège
                ticket.trip.release_seats(1)
            
            # Logger
            ActivityLog.objects.create(
                user=admin_user,
                action=ActivityLog.PAYMENT_REFUND,
                description=f"Remboursement paiement : {payment.transaction_id}",
                details={
                    'payment_id': str(payment.id),
                    'refund_amount': str(refund_amount),
                    'refund_reason': refund_reason,
                    'refund_transaction_id': result['refund_transaction_id']
                },
                severity=ActivityLog.SEVERITY_WARNING
            )
            
            # Notification
            from apps.notifications.models import Notification
            Notification.objects.create(
                user=payment.user,
                notification_type=Notification.EMAIL,
                category=Notification.REFUND_PROCESSED,
                title='Remboursement effectué',
                message=f'Votre remboursement de {refund_amount} FCFA a été effectué avec succès.',
                metadata={
                    'payment_id': str(payment.id),
                    'refund_amount': str(refund_amount)
                }
            )
        
        return result
    
    def get_payment_statistics(self, company=None, date_from=None, date_to=None):
        """
        Obtenir des statistiques sur les paiements
        
        Args:
            company: Filtrer par compagnie (optionnel)
            date_from: Date de début (optionnel)
            date_to: Date de fin (optionnel)
        
        Returns:
            dict: Statistiques
        """
        from django.db.models import Sum, Count, Avg, Q
        
        queryset = Payment.objects.all()# Filtrer par compagnie
        if company:
            queryset = queryset.filter(company=company)
        
        # Filtrer par date
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        # Calculer les statistiques
        stats = {
            'total_payments': queryset.count(),
            'total_amount': queryset.filter(
                status=Payment.SUCCESS
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00'),
            
            'successful_payments': queryset.filter(status=Payment.SUCCESS).count(),
            'failed_payments': queryset.filter(status=Payment.FAILED).count(),
            'pending_payments': queryset.filter(
                status__in=[Payment.PENDING, Payment.PROCESSING]
            ).count(),
            'refunded_payments': queryset.filter(status=Payment.REFUNDED).count(),
            
            'average_payment_amount': queryset.filter(
                status=Payment.SUCCESS
            ).aggregate(avg=Avg('amount'))['avg'] or Decimal('0.00'),
            
            'total_platform_commission': queryset.filter(
                status=Payment.SUCCESS
            ).aggregate(total=Sum('platform_commission'))['total'] or Decimal('0.00'),
            
            'total_company_amount': queryset.filter(
                status=Payment.SUCCESS
            ).aggregate(total=Sum('company_amount'))['total'] or Decimal('0.00'),
            
            'total_refunded_amount': queryset.filter(
                status=Payment.REFUNDED
            ).aggregate(total=Sum('refund_amount'))['total'] or Decimal('0.00'),
            
            # Par méthode de paiement
            'by_payment_method': {}
        }
        
        # Statistiques par méthode de paiement
        for method, label in Payment.PAYMENT_METHOD_CHOICES:
            method_stats = queryset.filter(payment_method=method)
            stats['by_payment_method'][method] = {
                'label': label,
                'count': method_stats.count(),
                'total_amount': method_stats.filter(
                    status=Payment.SUCCESS
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            }
        
        return stats
    
    @staticmethod
    def _get_client_ip(request):
        """Récupérer l'IP du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class MockPaymentTestHelper:
    """Helper pour tester les paiements en mode mocké"""
    
    def __init__(self):
        self.provider = CinetPayProvider()
    
    def simulate_payment_flow(self, ticket, payment_method='orange_money', phone_number=''):
        """
        Simuler un flow de paiement complet
        
        Args:
            ticket: Instance Ticket
            payment_method: Méthode de paiement
            phone_number: Numéro de téléphone
        
        Returns:
            dict: Résultat de la simulation
        """
        service = PaymentService()
        
        # 1. Créer le paiement
        payment = service.create_payment(
            ticket=ticket,
            payment_method=payment_method,
            phone_number=phone_number
        )
        
        # 2. Initialiser avec le provider
        init_result = service.initialize_payment_with_provider(
            payment=payment,
            ticket=ticket,
            return_url='http://localhost:3000/payment-success',
            notify_url='http://localhost:8000/api/v1/payments/webhook/'
        )
        
        if not init_result['success']:
            return {
                'success': False,
                'step': 'initialization',
                'message': init_result['message'],
                'payment': payment
            }
        
        # 3. Simuler le webhook de succès
        import time
        time.sleep(1)  # Simuler le délai de traitement
        
        webhook_result = self.provider.simulate_successful_payment(payment)
        
        # 4. Rafraîchir le paiement
        payment.refresh_from_db()
        
        return {
            'success': webhook_result['success'],
            'step': 'webhook',
            'message': 'Paiement simulé avec succès',
            'payment': payment,
            'init_result': init_result,
            'webhook_result': webhook_result
        }
    
    def simulate_failed_payment_flow(self, ticket, payment_method='orange_money', phone_number=''):
        """
        Simuler un flow de paiement échoué
        """
        service = PaymentService()
        
        # 1. Créer le paiement
        payment = service.create_payment(
            ticket=ticket,
            payment_method=payment_method,
            phone_number=phone_number
        )
        
        # 2. Initialiser avec le provider
        init_result = service.initialize_payment_with_provider(
            payment=payment,
            ticket=ticket,
            return_url='http://localhost:3000/payment-failed',
            notify_url='http://localhost:8000/api/v1/payments/webhook/'
        )
        
        # 3. Simuler le webhook d'échec
        import time
        time.sleep(1)
        
        webhook_result = self.provider.simulate_failed_payment(payment)
        
        # 4. Rafraîchir le paiement
        payment.refresh_from_db()
        
        return {
            'success': False,
            'step': 'webhook',
            'message': 'Paiement échoué (SIMULATION)',
            'payment': payment,
            'init_result': init_result,
            'webhook_result': webhook_result
        }
    
    def test_refund(self, payment, refund_amount=None):
        """
        Tester un remboursement
        """
        from apps.users.models import User
        
        if refund_amount is None:
            refund_amount = payment.amount
        
        # Créer un admin fictif pour le test
        admin = User.objects.filter(role='admin').first()
        if not admin:
            admin = User.objects.create_user(
                email='admin@test.com',
                password='testpass123',
                first_name='Test',
                last_name='Admin',
                phone_number='+225XXXXXXXX',
                role='admin'
            )
        
        service = PaymentService()
        result = service.process_refund(
            payment=payment,
            refund_amount=refund_amount,
            refund_reason='Test de remboursement',
            admin_user=admin
        )
        
        return result
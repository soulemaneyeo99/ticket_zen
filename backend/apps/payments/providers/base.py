"""
Classe de base pour les providers de paiement
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BasePaymentProvider(ABC):
    """Classe abstraite pour tous les providers de paiement"""
    
    def __init__(self):
        self.provider_name = self.__class__.__name__
    
    @abstractmethod
    def initialize_payment(self, payment, ticket, return_url, notify_url) -> Dict[str, Any]:
        """
        Initialiser un paiement
        
        Args:
            payment: Instance Payment
            ticket: Instance Ticket
            return_url: URL de retour après paiement
            notify_url: URL de notification webhook
        
        Returns:
            dict: {
                'success': bool,
                'transaction_id': str,
                'payment_url': str,
                'message': str
            }
        """
        pass
    
    @abstractmethod
    def check_payment_status(self, transaction_id) -> Dict[str, Any]:
        """
        Vérifier le statut d'un paiement
        
        Args:
            transaction_id: ID de transaction du provider
        
        Returns:
            dict: {
                'success': bool,
                'status': str,
                'amount': float,
                'transaction_id': str,
                'data': dict
            }
        """
        pass
    
    @abstractmethod
    def handle_webhook(self, webhook_data) -> Dict[str, Any]:
        """
        Traiter une notification webhook
        
        Args:
            webhook_data: Données du webhook
        
        Returns:
            dict: {
                'success': bool,
                'payment': Payment instance,
                'message': str
            }
        """
        pass
    
    @abstractmethod
    def refund_payment(self, payment, amount) -> Dict[str, Any]:
        """
        Rembourser un paiement
        
        Args:
            payment: Instance Payment
            amount: Montant à rembourser
        
        Returns:
            dict: {
                'success': bool,
                'refund_transaction_id': str,
                'message': str
            }
        """
        pass
    
    def validate_webhook_signature(self, webhook_data, signature) -> bool:
        """
        Valider la signature d'un webhook
        
        Args:
            webhook_data: Données du webhook
            signature: Signature à valider
        
        Returns:
            bool: True si valide
        """
        # À implémenter dans chaque provider
        return True
    
    def log_transaction(self, action, details):
        """Logger une transaction"""
        from apps.logs.models import ActivityLog
        
        ActivityLog.objects.create(
            action=ActivityLog.PAYMENT_INIT if action == 'init' else ActivityLog.PAYMENT_SUCCESS,
            description=f"Transaction {self.provider_name}: {action}",
            details=details,
            severity=ActivityLog.SEVERITY_INFO
        )
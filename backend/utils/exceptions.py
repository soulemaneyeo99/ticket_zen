"""
Gestion centralisée des exceptions
"""
from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404


class TicketZenException(APIException):
    """Exception de base pour Ticket Zen"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Une erreur est survenue'
    default_code = 'error'


class TicketNotAvailableException(TicketZenException):
    """Exception quand un ticket n'est pas disponible"""
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Ce ticket n\'est plus disponible'
    default_code = 'ticket_not_available'


class PaymentFailedException(TicketZenException):
    """Exception quand un paiement échoue"""
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = 'Le paiement a échoué'
    default_code = 'payment_failed'


class CompanyNotApprovedException(TicketZenException):
    """Exception quand une compagnie n'est pas approuvée"""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Votre compagnie doit être approuvée'
    default_code = 'company_not_approved'


class TripFullException(TicketZenException):
    """Exception quand un voyage est complet"""
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Ce voyage est complet'
    default_code = 'trip_full'


class InvalidQRCodeException(TicketZenException):
    """Exception pour QR code invalide"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'QR code invalide'
    default_code = 'invalid_qr_code'


class MaintenanceModeException(TicketZenException):
    """Exception en mode maintenance"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'La plateforme est en maintenance'
    default_code = 'maintenance_mode'


def custom_exception_handler(exc, context):
    """
    Handler personnalisé pour les exceptions
    """
    # Appeler le handler par défaut de DRF
    response = exception_handler(exc, context)
    
    # Si DRF n'a pas géré l'exception
    if response is None:
        # Gérer les exceptions Django
        if isinstance(exc, DjangoValidationError):
            response_data = {
                'error': 'Erreur de validation',
                'details': exc.message_dict if hasattr(exc, 'message_dict') else str(exc),
                'code': 'validation_error'
            }
            from rest_framework.response import Response
            response = Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        elif isinstance(exc, Http404):
            response_data = {
                'error': 'Ressource introuvable',
                'details': str(exc),
                'code': 'not_found'
            }
            from rest_framework.response import Response
            response = Response(response_data, status=status.HTTP_404_NOT_FOUND)
    
    # Ajouter des informations supplémentaires à la réponse
    if response is not None:
        # Format standardisé des erreurs
        if 'detail' in response.data:
            response.data = {
                'error': response.data.get('detail'),
                'code': getattr(exc, 'default_code', 'error'),
                'status_code': response.status_code
            }
        elif isinstance(response.data, dict):
            # Si c'est déjà un dict, ajouter le code
            if 'error' not in response.data:
                response.data['error'] = 'Une erreur est survenue'
            if 'code' not in response.data:
                response.data['code'] = getattr(exc, 'default_code', 'error')
            response.data['status_code'] = response.status_code
    
    return response
"""
Views pour la gestion des paiements
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.db import transaction
from django.conf import settings

from apps.payments.models import Payment
from apps.payments.serializers import (
    PaymentInitSerializer,
    PaymentDetailSerializer,
    PaymentListSerializer,
    PaymentWebhookSerializer,
    PaymentRefundSerializer
)
from apps.tickets.models import Ticket
from apps.users.permissions import CanManagePayment, IsAdminGlobal
from apps.logs.models import ActivityLog
from apps.payments.providers.cinetpay import CinetPayProvider
from utils.pagination import StandardResultsSetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour la gestion des paiements (lecture seule + actions)"""
    
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated, CanManagePayment]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'payment_method', 'user', 'company']
    search_fields = ['transaction_id', 'provider_transaction_id']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Retourner le serializer approprié"""
        if self.action == 'list':
            return PaymentListSerializer
        return PaymentDetailSerializer
    
    def get_queryset(self):
        """Filtrer selon le rôle"""
        queryset = super().get_queryset().select_related(
            'user', 'trip', 'company'
        )
        
        # Les admins voient tous les paiements
        if self.request.user.role == 'admin':
            return queryset
        
        # Les compagnies voient leurs paiements
        if self.request.user.role == 'compagnie' and self.request.user.company:
            return queryset.filter(company=self.request.user.company)
        
        # Les voyageurs voient leurs propres paiements
        return queryset.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'], url_path='initialize')
    def initialize(self, request):
        """Initialiser un paiement"""
        serializer = PaymentInitSerializer(data=request.data)
        
        if serializer.is_valid():
            ticket_id = serializer.validated_data['ticket_id']
            payment_method = serializer.validated_data['payment_method']
            phone_number = serializer.validated_data.get('phone_number', '')
            
            try:
                ticket = Ticket.objects.select_related('trip', 'trip__company').get(
                    id=ticket_id,
                    passenger=request.user
                )
            except Ticket.DoesNotExist:
                return Response(
                    {'error': 'Ticket introuvable'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Vérifier que le ticket n'est pas déjà payé
            if ticket.is_paid:
                return Response(
                    {'error': 'Ce ticket a déjà été payé'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            with transaction.atomic():
                # Créer le paiement
                payment = Payment.objects.create(
                    user=request.user,
                    trip=ticket.trip,
                    company=ticket.trip.company,
                    amount=ticket.total_amount,
                    payment_method=payment_method,
                    phone_number=phone_number,
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                # Associer le paiement au ticket
                ticket.payment = payment
                ticket.save()
                
                # Initialiser le paiement avec CinetPay
                provider = CinetPayProvider()
                result = provider.initialize_payment(
                    payment=payment,
                    ticket=ticket,
                    return_url=request.data.get('return_url', ''),
                    notify_url=settings.CINETPAY_NOTIFY_URL
                )
                
                if result['success']:
                    payment.provider_transaction_id = result.get('transaction_id', '')
                    payment.payment_url = result.get('payment_url', '')
                    payment.status = Payment.PROCESSING
                    payment.provider_response = result
                    payment.save()
                    
                    return Response({
                        'message': 'Paiement initialisé avec succès',
                        'payment': PaymentDetailSerializer(payment).data,
                        'payment_url': payment.payment_url
                    }, status=status.HTTP_201_CREATED)
                else:
                    payment.status = Payment.FAILED
                    payment.provider_response = result
                    payment.save()
                    
                    return Response({
                        'error': result.get('message', 'Erreur lors de l\'initialisation du paiement')
                    }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='webhook', permission_classes=[AllowAny])
    def webhook(self, request):
        """Webhook pour recevoir les notifications de paiement"""
        serializer = PaymentWebhookSerializer(data=request.data)
        
        if serializer.is_valid():
            provider = CinetPayProvider()
            result = provider.handle_webhook(serializer.validated_data)
            
            if result['success']:
                return Response({'message': 'Webhook traité avec succès'})
            else:
                return Response(
                    {'error': result.get('message', 'Erreur traitement webhook')},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='refund', permission_classes=[IsAdminGlobal])
    def refund(self, request, pk=None):
        """Rembourser un paiement (admin seulement)"""
        payment = self.get_object()
        
        serializer = PaymentRefundSerializer(
            data=request.data,
            context={'payment': payment}
        )
        
        if serializer.is_valid():
            refund_amount = serializer.validated_data['refund_amount']
            refund_reason = serializer.validated_data['refund_reason']
            
            with transaction.atomic():
                # Initier le remboursement
                provider = CinetPayProvider()
                result = provider.refund_payment(payment, refund_amount)
                
                if result['success']:
                    payment.status = Payment.REFUNDED
                    payment.refund_amount = refund_amount
                    payment.refund_reason = refund_reason
                    payment.refunded_at = timezone.now()
                    payment.refund_transaction_id = result.get('refund_transaction_id', '')
                    payment.save()
                    
                    # Mettre à jour le ticket
                    if hasattr(payment, 'ticket'):
                        payment.ticket.status = Ticket.REFUNDED
                        payment.ticket.refund_amount = refund_amount
                        payment.ticket.save()
                    
                    # Logger le remboursement
                    ActivityLog.objects.create(
                        user=request.user,
                        action=ActivityLog.PAYMENT_REFUND,
                        description=f"Remboursement paiement : {payment.transaction_id}",
                        details={
                            'payment_id': str(payment.id),
                            'refund_amount': str(refund_amount),
                            'reason': refund_reason
                        },
                        content_type='Payment',
                        object_id=str(payment.id),
                        severity=ActivityLog.SEVERITY_WARNING
                    )
                    
                    return Response({
                        'message': 'Remboursement effectué avec succès',
                        'payment': PaymentDetailSerializer(payment).data
                    })
                else:
                    return Response({
                        'error': result.get('message', 'Erreur lors du remboursement')
                    }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='my-payments')
    def my_payments(self, request):
        """Paiements de l'utilisateur connecté"""
        queryset = self.get_queryset().filter(user=request.user)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PaymentListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PaymentListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @staticmethod
    def get_client_ip(request):
        """Récupérer l'IP du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
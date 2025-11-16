"""
Views pour la gestion des tickets
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import transaction

from apps.tickets.models import Ticket
from apps.tickets.serializers import (
    TicketCreateSerializer,
    TicketDetailSerializer,
    TicketListSerializer,
    TicketCancellationSerializer,
    TicketVerificationSerializer
)
from apps.users.permissions import IsVoyageur, CanManageTicket
from apps.logs.models import ActivityLog
from utils.pagination import StandardResultsSetPagination
from utils.qr_generator import QRCodeGenerator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class TicketViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des tickets"""
    
    queryset = Ticket.objects.all()
    permission_classes = [IsAuthenticated, CanManageTicket]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'is_paid', 'trip', 'passenger']
    search_fields = ['ticket_number', 'passenger_first_name', 'passenger_last_name']
    ordering_fields = ['created_at', 'trip__departure_datetime']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Retourner le serializer approprié"""
        if self.action == 'create':
            return TicketCreateSerializer
        elif self.action == 'list':
            return TicketListSerializer
        elif self.action == 'cancel':
            return TicketCancellationSerializer
        elif self.action == 'verify':
            return TicketVerificationSerializer
        return TicketDetailSerializer
    
    def get_queryset(self):
        """Filtrer selon le rôle"""
        queryset = super().get_queryset().select_related(
            'trip', 'trip__company', 'trip__departure_city', 'trip__arrival_city',
            'passenger', 'payment'
        )
        
        # Les admins voient tous les tickets
        if self.request.user.role == 'admin':
            return queryset
        
        # Les compagnies voient les tickets de leurs voyages
        if self.request.user.role == 'compagnie' and self.request.user.company:
            return queryset.filter(trip__company=self.request.user.company)
        
        # Les embarqueurs voient les tickets des voyages de leur compagnie
        if self.request.user.role == 'embarqueur' and self.request.user.company:
            return queryset.filter(trip__company=self.request.user.company)
        
        # Les voyageurs voient leurs propres tickets
        return queryset.filter(passenger=self.request.user)
    
    def get_permissions(self):
        """Permissions dynamiques"""
        if self.action == 'create':
            return [IsVoyageur()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [CanManageTicket()]
        return [IsAuthenticated()]
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Créer un ticket (réservation)"""
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            ticket = serializer.save()
            
            # Générer le QR code (sera mis à jour après paiement)
            # Pour l'instant, on le laisse vide
            
            return Response({
                'message': 'Réservation créée avec succès',
                'ticket': TicketDetailSerializer(ticket).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        """Annuler un ticket"""
        ticket = self.get_object()
        
        # Vérifier que l'utilisateur est le propriétaire
        if ticket.passenger != request.user:
            return Response(
                {'error': 'Vous ne pouvez pas annuler ce ticket'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = TicketCancellationSerializer(
            data=request.data,
            context={'ticket': ticket}
        )
        
        if serializer.is_valid():
            with transaction.atomic():
                # Annuler le ticket
                ticket.status = Ticket.CANCELLED
                ticket.cancelled_at = timezone.now()
                ticket.cancellation_reason = serializer.validated_data['cancellation_reason']
                ticket.save()
                
                # Logger l'annulation
                ActivityLog.objects.create(
                    user=request.user,
                    action=ActivityLog.TICKET_CANCEL,
                    description=f"Annulation ticket : {ticket.ticket_number}",
                    details={
                        'ticket_id': str(ticket.id),
                        'ticket_number': ticket.ticket_number,
                        'reason': ticket.cancellation_reason
                    },
                    content_type='Ticket',
                    object_id=str(ticket.id),
                    severity=ActivityLog.SEVERITY_INFO
                )
                
                # Initier le remboursement si payé
                if ticket.is_paid and ticket.payment:
                    # Le remboursement sera géré dans le module payments
                    pass
            
            return Response({
                'message': 'Ticket annulé avec succès',
                'ticket': TicketDetailSerializer(ticket).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='confirm')
    def confirm(self, request, pk=None):
        """Confirmer un ticket après paiement"""
        ticket = self.get_object()
        
        if ticket.status != Ticket.PENDING:
            return Response(
                {'error': 'Ce ticket ne peut pas être confirmé'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not ticket.is_paid:
            return Response(
                {'error': 'Le paiement n\'a pas été effectué'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Confirmer le ticket
        ticket.status = Ticket.CONFIRMED
        ticket.confirmed_at = timezone.now()
        
        # Générer le QR code sécurisé
        qr_generator = QRCodeGenerator()
        qr_data = qr_generator.generate_qr_code(ticket)
        
        ticket.qr_code = qr_data['token']
        ticket.qr_code_image = qr_data['image']
        ticket.save()
        
        # Logger la confirmation
        ActivityLog.objects.create(
            user=request.user,
            action=ActivityLog.TICKET_CONFIRM,
            description=f"Confirmation ticket : {ticket.ticket_number}",
            details={
                'ticket_id': str(ticket.id),
                'ticket_number': ticket.ticket_number
            },
            content_type='Ticket',
            object_id=str(ticket.id),
            severity=ActivityLog.SEVERITY_INFO
        )
        
        return Response({
            'message': 'Ticket confirmé avec succès',
            'ticket': TicketDetailSerializer(ticket).data
        })
    
    @action(detail=False, methods=['post'], url_path='verify')
    def verify(self, request):
        """Vérifier la validité d'un QR code"""
        serializer = TicketVerificationSerializer(data=request.data)
        
        if serializer.is_valid():
            qr_generator = QRCodeGenerator()
            
            try:
                # Décoder et vérifier le QR code
                decoded_data = qr_generator.decode_qr_code(
                    serializer.validated_data['qr_code_data']
                )
                
                # Récupérer le ticket
                ticket = Ticket.objects.select_related(
                    'trip', 'trip__company', 'passenger'
                ).get(id=decoded_data['ticket_id'])
                
                # Vérifier la validité
                is_valid = True
                error_message = None
                
                if ticket.status == Ticket.USED:
                    is_valid = False
                    error_message = 'Ce ticket a déjà été utilisé'
                elif ticket.status != Ticket.CONFIRMED:
                    is_valid = False
                    error_message = 'Ce ticket n\'est pas confirmé'
                elif str(ticket.trip.id) != decoded_data.get('trip_id'):
                    is_valid = False
                    error_message = 'Ce ticket n\'est pas valide pour ce voyage'
                elif ticket.trip.departure_datetime < timezone.now() - timezone.timedelta(hours=24):
                    is_valid = False
                    error_message = 'Ce ticket a expiré'
                
                return Response({
                    'is_valid': is_valid,
                    'error_message': error_message,
                    'ticket': TicketDetailSerializer(ticket).data if is_valid else None
                })
            
            except Ticket.DoesNotExist:
                return Response({
                    'is_valid': False,
                    'error_message': 'Ticket introuvable',
                    'ticket': None
                })
            except Exception as e:
                return Response({
                    'is_valid': False,
                    'error_message': f'QR code invalide : {str(e)}',
                    'ticket': None
                })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='my-tickets')
    def my_tickets(self, request):
        """Tickets de l'utilisateur connecté"""
        queryset = self.get_queryset().filter(passenger=request.user)
        
        # Filtrer par statut si fourni
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TicketListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = TicketListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='upcoming')
    def upcoming(self, request):
        """Tickets à venir de l'utilisateur"""
        queryset = self.get_queryset().filter(
            passenger=request.user,
            status__in=[Ticket.PENDING, Ticket.CONFIRMED],
            trip__departure_datetime__gte=timezone.now()
        ).order_by('trip__departure_datetime')
        
        serializer = TicketListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='history')
    def history(self, request):
        """Historique des tickets de l'utilisateur"""
        queryset = self.get_queryset().filter(
            passenger=request.user,
            trip__departure_datetime__lt=timezone.now()
        ).order_by('-trip__departure_datetime')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TicketListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = TicketListSerializer(queryset, many=True)
        return Response(serializer.data)
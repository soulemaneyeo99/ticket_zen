"""
Signaux pour le modèle Ticket
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from apps.tickets.models import Ticket
from apps.logs.models import ActivityLog
from apps.notifications.models import Notification


@receiver(pre_save, sender=Ticket)
def ticket_pre_save(sender, instance, **kwargs):
    """Actions avant sauvegarde d'un ticket"""
    
    # Si le statut passe à confirmé, définir confirmed_at
    if instance.pk:
        try:
            old_instance = Ticket.objects.get(pk=instance.pk)
            if old_instance.status != Ticket.CONFIRMED and instance.status == Ticket.CONFIRMED:
                instance.confirmed_at = timezone.now()
            
            # Si annulé, définir cancelled_at
            if old_instance.status != Ticket.CANCELLED and instance.status == Ticket.CANCELLED:
                instance.cancelled_at = timezone.now()
        except Ticket.DoesNotExist:
            pass


@receiver(post_save, sender=Ticket)
def ticket_post_save(sender, instance, created, **kwargs):
    """Actions après création/modification d'un ticket"""
    
    if created:
        # Décrémenter les places disponibles du voyage
        instance.trip.reserve_seats(1)
        
        # Logger la création
        ActivityLog.objects.create(
            user=instance.passenger,
            action=ActivityLog.TICKET_CREATE,
            description=f"Nouveau ticket créé : {instance.ticket_number}",
            details={
                'ticket_id': str(instance.id),
                'ticket_number': instance.ticket_number,
                'trip_id': str(instance.trip.id),
                'seat_number': instance.seat_number,
                'price': str(instance.total_amount)
            },
            content_type='Ticket',
            object_id=str(instance.id),
            severity=ActivityLog.SEVERITY_INFO
        )
    
    else:
        # Vérifier si le statut a changé
        old_instance = Ticket.objects.get(pk=instance.pk)
        
        if old_instance.status != instance.status:
            # Logger le changement de statut
            ActivityLog.objects.create(
                user=instance.passenger,
                action=ActivityLog.TICKET_CONFIRM if instance.status == Ticket.CONFIRMED else ActivityLog.TICKET_CANCEL,
                description=f"Ticket {instance.ticket_number} : {old_instance.get_status_display()} → {instance.get_status_display()}",
                details={
                    'ticket_id': str(instance.id),
                    'ticket_number': instance.ticket_number,
                    'old_status': old_instance.status,
                    'new_status': instance.status
                },
                content_type='Ticket',
                object_id=str(instance.id),
                severity=ActivityLog.SEVERITY_INFO
            )
            
            # Créer notification selon le statut
            if instance.status == Ticket.CONFIRMED:
                Notification.objects.create(
                    user=instance.passenger,
                    notification_type=Notification.EMAIL,
                    category=Notification.BOOKING_CONFIRMATION,
                    title='Réservation confirmée',
                    message=f'Votre réservation pour {instance.trip} a été confirmée.',
                    metadata={
                        'ticket_id': str(instance.id),
                        'ticket_number': instance.ticket_number
                    },
                    recipient_email=instance.passenger_email
                )
            
            elif instance.status == Ticket.CANCELLED:
                # Libérer le siège
                instance.trip.release_seats(1)
                
                Notification.objects.create(
                    user=instance.passenger,
                    notification_type=Notification.EMAIL,
                    category=Notification.TRIP_CANCELLED,
                    title='Réservation annulée',
                    message=f'Votre réservation pour {instance.trip} a été annulée.',
                    metadata={
                        'ticket_id': str(instance.id),
                        'ticket_number': instance.ticket_number
                    },
                    recipient_email=instance.passenger_email
                )
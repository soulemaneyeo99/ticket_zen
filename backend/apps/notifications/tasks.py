"""
Tâches Celery pour les notifications
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from apps.notifications.models import Notification
from apps.logs.models import ActivityLog


@shared_task(bind=True, max_retries=3)
def send_email_notification(self, notification_id):
    """
    Envoyer une notification par email
    """
    try:
        notification = Notification.objects.get(id=notification_id)
        
        # Préparer le contenu
        subject = notification.title
        
        if notification.html_content:
            html_message = notification.html_content
            message = strip_tags(html_message)
        else:
            message = notification.message
            html_message = None
        
        # Déterminer le destinataire
        recipient_email = notification.recipient_email or notification.user.email
        
        # Envoyer l'email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False
        )
        
        # Mettre à jour le statut
        notification.status = Notification.SENT
        notification.sent_at = timezone.now()
        notification.save()
        
        return f"Email envoyé à {recipient_email}"
    
    except Notification.DoesNotExist:
        return f"Notification {notification_id} introuvable"
    
    except Exception as exc:
        notification.attempts += 1
        notification.error_message = str(exc)
        
        if notification.attempts >= notification.max_attempts:
            notification.status = Notification.FAILED
        
        notification.save()
        
        # Réessayer si pas au max
        if notification.attempts < notification.max_attempts:
            raise self.retry(exc=exc, countdown=60 * notification.attempts)
        
        return f"Échec après {notification.attempts} tentatives: {str(exc)}"


@shared_task(bind=True, max_retries=3)
def send_sms_notification(self, notification_id):
    """
    Envoyer une notification par SMS
    """
    try:
        notification = Notification.objects.get(id=notification_id)
        
        # Déterminer le destinataire
        recipient_phone = notification.recipient_phone or notification.user.phone_number
        
        # TODO: Intégrer avec un provider SMS réel
        # Pour l'instant, on simule l'envoi
        
        from apps.core.models import PlatformSettings
        settings_obj = PlatformSettings.load()
        
        if settings_obj.send_sms_notifications:
            # Simuler l'envoi SMS
            print(f"📱 SMS envoyé à {recipient_phone}: {notification.message[:160]}")
            
            # Mettre à jour le statut
            notification.status = Notification.SENT
            notification.sent_at = timezone.now()
            notification.save()
            
            return f"SMS envoyé à {recipient_phone}"
        else:
            notification.status = Notification.FAILED
            notification.error_message = "Notifications SMS désactivées"
            notification.save()
            return "SMS désactivés"
    
    except Notification.DoesNotExist:
        return f"Notification {notification_id} introuvable"
    
    except Exception as exc:
        notification.attempts += 1
        notification.error_message = str(exc)
        
        if notification.attempts >= notification.max_attempts:
            notification.status = Notification.FAILED
        
        notification.save()
        
        if notification.attempts < notification.max_attempts:
            raise self.retry(exc=exc, countdown=60 * notification.attempts)
        
        return f"Échec SMS: {str(exc)}"


@shared_task
def send_trip_reminders():
    """
    Envoyer des rappels pour les voyages à venir
    """
    from django.utils import timezone
    from datetime import timedelta
    from apps.tickets.models import Ticket
    from apps.core.models import PlatformSettings
    
    settings = PlatformSettings.load()
    reminder_hours = settings.trip_reminder_hours_before
    
    # Calculer la fenêtre de temps
    now = timezone.now()
    reminder_time = now + timedelta(hours=reminder_hours)
    
    # Trouver les tickets pour les voyages dans la fenêtre
    tickets = Ticket.objects.filter(
        status=Ticket.CONFIRMED,
        trip__departure_datetime__gte=now,
        trip__departure_datetime__lte=reminder_time
    ).select_related('trip', 'passenger')
    
    sent_count = 0
    
    for ticket in tickets:
        # Vérifier si un rappel n'a pas déjà été envoyé
        existing_notification = Notification.objects.filter(
            user=ticket.passenger,
            category=Notification.TRIP_REMINDER,
            metadata__ticket_id=str(ticket.id)
        ).exists()
        
        if not existing_notification:
            # Créer la notification
            notification = Notification.objects.create(
                user=ticket.passenger,
                notification_type=Notification.EMAIL,
                category=Notification.TRIP_REMINDER,
                title='Rappel de voyage',
                message=f'Votre voyage {ticket.trip.departure_city.name} → {ticket.trip.arrival_city.name} est prévu pour {ticket.trip.departure_datetime.strftime("%d/%m/%Y à %H:%M")}.',
                metadata={
                    'ticket_id': str(ticket.id),
                    'trip_id': str(ticket.trip.id)
                },
                recipient_email=ticket.passenger_email
            )
            
            # Envoyer de manière asynchrone
            send_email_notification.delay(notification.id)
            sent_count += 1
    
    return f"{sent_count} rappels envoyés"


@shared_task
def cleanup_old_notifications():
    """
    Nettoyer les anciennes notifications
    """
    from django.utils import timezone
    from datetime import timedelta
    
    # Supprimer les notifications lues de plus de 30 jours
    cutoff_date = timezone.now() - timedelta(days=30)
    
    deleted_count = Notification.objects.filter(
        status=Notification.READ,
        read_at__lt=cutoff_date
    ).delete()[0]
    
    return f"{deleted_count} notifications supprimées"
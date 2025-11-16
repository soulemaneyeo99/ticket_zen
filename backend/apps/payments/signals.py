"""
Signaux pour le modèle Payment
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from apps.payments.models import Payment
from apps.logs.models import ActivityLog
from apps.notifications.models import Notification


@receiver(post_save, sender=Payment)
def payment_post_save(sender, instance, created, **kwargs):
    """Actions après création/modification d'un paiement"""
    
    if created:
        # Logger l'initialisation du paiement
        ActivityLog.objects.create(
            user=instance.user,
            action=ActivityLog.PAYMENT_INIT,
            description=f"Paiement initialisé : {instance.transaction_id}",
            details={
                'payment_id': str(instance.id),
                'transaction_id': instance.transaction_id,
                'amount': str(instance.amount),
                'payment_method': instance.payment_method
            },
            content_type='Payment',
            object_id=str(instance.id),
            severity=ActivityLog.SEVERITY_INFO,
            ip_address=instance.ip_address
        )
    
    else:
        # Vérifier si le statut a changé
        old_instance = Payment.objects.get(pk=instance.pk)
        
        if old_instance.status != instance.status:
            # Logger le changement de statut
            if instance.status == Payment.SUCCESS:
                instance.completed_at = timezone.now()
                instance.save(update_fields=['completed_at'])
                
                ActivityLog.objects.create(
                    user=instance.user,
                    action=ActivityLog.PAYMENT_SUCCESS,
                    description=f"Paiement réussi : {instance.transaction_id}",
                    details={
                        'payment_id': str(instance.id),
                        'transaction_id': instance.transaction_id,
                        'amount': str(instance.amount)
                    },
                    content_type='Payment',
                    object_id=str(instance.id),
                    severity=ActivityLog.SEVERITY_INFO,
                    ip_address=instance.ip_address
                )
                
                # Notification de succès
                Notification.objects.create(
                    user=instance.user,
                    notification_type=Notification.EMAIL,
                    category=Notification.PAYMENT_SUCCESS,
                    title='Paiement réussi',
                    message=f'Votre paiement de {instance.amount} XOF a été effectué avec succès.',
                    metadata={
                        'payment_id': str(instance.id),
                        'transaction_id': instance.transaction_id,
                        'amount': str(instance.amount)
                    }
                )
                
                # Mettre à jour les statistiques de la compagnie
                instance.company.increment_stats(
                    ticket_count=1,
                    revenue=float(instance.company_amount)
                )
                
            elif instance.status == Payment.FAILED:
                ActivityLog.objects.create(
                    user=instance.user,
                    action=ActivityLog.PAYMENT_FAILED,
                    description=f"Paiement échoué : {instance.transaction_id}",
                    details={
                        'payment_id': str(instance.id),
                        'transaction_id': instance.transaction_id,
                        'amount': str(instance.amount),
                        'error': instance.provider_response
                    },
                    content_type='Payment',
                    object_id=str(instance.id),
                    severity=ActivityLog.SEVERITY_WARNING,
                    ip_address=instance.ip_address
                )
                
                # Notification d'échec
                Notification.objects.create(
                    user=instance.user,
                    notification_type=Notification.EMAIL,
                    category=Notification.PAYMENT_FAILED,
                    title='Paiement échoué',
                    message=f'Votre paiement de {instance.amount} XOF a échoué. Veuillez réessayer.',
                    metadata={
                        'payment_id': str(instance.id),
                        'transaction_id': instance.transaction_id
                    }
                )
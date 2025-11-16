"""
Signaux pour le modèle User
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.users.models import User
from apps.logs.models import ActivityLog


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """Actions après création/modification d'un utilisateur"""
    
    if created:
        # Logger la création
        ActivityLog.objects.create(
            user=instance,
            action=ActivityLog.USER_REGISTER,
            description=f"Nouvel utilisateur créé : {instance.email} ({instance.get_role_display()})",
            details={
                'user_id': str(instance.id),
                'email': instance.email,
                'role': instance.role,
                'phone_number': instance.phone_number
            },
            content_type='User',
            object_id=str(instance.id),
            severity=ActivityLog.SEVERITY_INFO
        )
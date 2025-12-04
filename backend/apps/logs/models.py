"""
Modèle ActivityLog pour logs immuables
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField


class ActivityLog(models.Model):
    """Log immuable de toutes les actions sensibles"""
    
    # Types d'actions
    USER_LOGIN = 'user_login'
    USER_LOGOUT = 'user_logout'
    USER_REGISTER = 'user_register'
    USER_UPDATE = 'user_update'
    USER_DELETE = 'user_delete'
    
    TICKET_CREATE = 'ticket_create'
    TICKET_CONFIRM = 'ticket_confirm'
    TICKET_CANCEL = 'ticket_cancel'
    TICKET_SCAN = 'ticket_scan'
    
    PAYMENT_INIT = 'payment_init'
    PAYMENT_SUCCESS = 'payment_success'
    PAYMENT_FAILED = 'payment_failed'
    PAYMENT_REFUND = 'payment_refund'
    
    TRIP_CREATE = 'trip_create'
    TRIP_UPDATE = 'trip_update'
    TRIP_DELETE = 'trip_delete'
    TRIP_CANCEL = 'trip_cancel'
    
    COMPANY_CREATE = 'company_create'
    COMPANY_APPROVE = 'company_approve'
    COMPANY_REJECT = 'company_reject'
    COMPANY_SUSPEND = 'company_suspend'
    
    ADMIN_ACTION = 'admin_action'
    
    ACTION_CHOICES = [
        (USER_LOGIN, _('Connexion utilisateur')),
        (USER_LOGOUT, _('Déconnexion utilisateur')),
        (USER_REGISTER, _('Inscription utilisateur')),
        (USER_UPDATE, _('Modification utilisateur')),
        (USER_DELETE, _('Suppression utilisateur')),
        (TICKET_CREATE, _('Création ticket')),
        (TICKET_CONFIRM, _('Confirmation ticket')),
        (TICKET_CANCEL, _('Annulation ticket')),
        (TICKET_SCAN, _('Scan ticket')),
        (PAYMENT_INIT, _('Initialisation paiement')),
        (PAYMENT_SUCCESS, _('Paiement réussi')),
        (PAYMENT_FAILED, _('Paiement échoué')),
        (PAYMENT_REFUND, _('Remboursement')),
        (TRIP_CREATE, _('Création voyage')),
        (TRIP_UPDATE, _('Modification voyage')),
        (TRIP_DELETE, _('Suppression voyage')),
        (TRIP_CANCEL, _('Annulation voyage')),
        (COMPANY_CREATE, _('Création compagnie')),
        (COMPANY_APPROVE, _('Approbation compagnie')),
        (COMPANY_REJECT, _('Rejet compagnie')),
        (COMPANY_SUSPEND, _('Suspension compagnie')),
        (ADMIN_ACTION, _('Action admin')),
    ]
    
    # Relations (nullable car log doit persister même si objet supprimé)
    user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activity_logs',
        verbose_name=_('utilisateur')
    )
    
    # Informations de l'action
    action = models.CharField(
        _('action'),
        max_length=50,
        choices=ACTION_CHOICES,
        db_index=True
    )
    
    description = models.TextField(_('description'))
    
    # Détails JSON (données avant/après, metadata)
    details = models.JSONField(
        _('détails'),
        default=dict,
        blank=True
    )
    
    # Contexte technique
    ip_address = models.GenericIPAddressField(_('adresse IP'), null=True, blank=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    
    # Référence aux objets concernés
    content_type = models.CharField(_('type d\'objet'), max_length=100, blank=True)
    object_id = models.CharField(_('ID objet'), max_length=255, blank=True, db_index=True)
    
    # Niveau de sévérité
    SEVERITY_INFO = 'info'
    SEVERITY_WARNING = 'warning'
    SEVERITY_ERROR = 'error'
    SEVERITY_CRITICAL = 'critical'
    
    SEVERITY_CHOICES = [
        (SEVERITY_INFO, _('Info')),
        (SEVERITY_WARNING, _('Avertissement')),
        (SEVERITY_ERROR, _('Erreur')),
        (SEVERITY_CRITICAL, _('Critique')),
    ]
    
    severity = models.CharField(
        _('sévérité'),
        max_length=20,
        choices=SEVERITY_CHOICES,
        default=SEVERITY_INFO,
        db_index=True
    )
    
    # Tags pour recherche avancée
    tags = ArrayField(
        models.CharField(max_length=50),
        default=list,
        blank=True,
        verbose_name=_('tags')
    )
    
    # Timestamp précis avec timezone
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'activity_logs'
        verbose_name = _('log d\'activité')
        verbose_name_plural = _('logs d\'activité')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'action', 'created_at']),
            models.Index(fields=['action', 'created_at']),
            models.Index(fields=['severity', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
            models.Index(fields=['object_id', 'content_type']),
        ]
        
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.created_at.strftime('%d/%m/%Y %H:%M:%S')}"
    
    def save(self, *args, **kwargs):
        # Ne permettre que la création, pas la modification
        if self.pk:
            raise ValueError(_("Les logs ne peuvent pas être modifiés"))
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Empêcher la suppression
        raise ValueError(_("Les logs ne peuvent pas être supprimés"))
    
    
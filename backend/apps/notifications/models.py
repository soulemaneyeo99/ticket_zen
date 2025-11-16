"""
Modèle Notification pour gérer les notifications
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    """Notification envoyée aux utilisateurs"""
    
    # Types de notification
    EMAIL = 'email'
    SMS = 'sms'
    IN_APP = 'in_app'
    PUSH = 'push'
    
    TYPE_CHOICES = [
        (EMAIL, _('Email')),
        (SMS, _('SMS')),
        (IN_APP, _('In-app')),
        (PUSH, _('Push')),
    ]
    
    # Catégories
    BOOKING_CONFIRMATION = 'booking_confirmation'
    PAYMENT_SUCCESS = 'payment_success'
    PAYMENT_FAILED = 'payment_failed'
    TRIP_REMINDER = 'trip_reminder'
    TRIP_CANCELLED = 'trip_cancelled'
    REFUND_PROCESSED = 'refund_processed'
    ACCOUNT_VERIFICATION = 'account_verification'
    PASSWORD_RESET = 'password_reset'
    COMPANY_APPROVED = 'company_approved'
    COMPANY_REJECTED = 'company_rejected'
    GENERAL = 'general'
    
    CATEGORY_CHOICES = [
        (BOOKING_CONFIRMATION, _('Confirmation réservation')),
        (PAYMENT_SUCCESS, _('Paiement réussi')),
        (PAYMENT_FAILED, _('Paiement échoué')),
        (TRIP_REMINDER, _('Rappel voyage')),
        (TRIP_CANCELLED, _('Voyage annulé')),
        (REFUND_PROCESSED, _('Remboursement traité')),
        (ACCOUNT_VERIFICATION, _('Vérification compte')),
        (PASSWORD_RESET, _('Réinitialisation mot de passe')),
        (COMPANY_APPROVED, _('Compagnie approuvée')),
        (COMPANY_REJECTED, _('Compagnie rejetée')),
        (GENERAL, _('Général')),
    ]
    
    # Statuts
    PENDING = 'pending'
    SENT = 'sent'
    FAILED = 'failed'
    READ = 'read'
    
    STATUS_CHOICES = [
        (PENDING, _('En attente')),
        (SENT, _('Envoyé')),
        (FAILED, _('Échoué')),
        (READ, _('Lu')),
    ]
    
    # Relations
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('utilisateur')
    )
    
    # Informations notification
    notification_type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPE_CHOICES,
        db_index=True
    )
    
    category = models.CharField(
        _('catégorie'),
        max_length=50,
        choices=CATEGORY_CHOICES,
        default=GENERAL,
        db_index=True
    )
    
    title = models.CharField(_('titre'), max_length=255)
    message = models.TextField(_('message'))
    
    # Contenu riche (HTML pour emails)
    html_content = models.TextField(_('contenu HTML'), blank=True)
    
    # Données additionnelles
    metadata = models.JSONField(
        _('métadonnées'),
        default=dict,
        blank=True,
        help_text=_('Données additionnelles liées à la notification')
    )
    
    # Lien d'action
    action_url = models.URLField(_('URL d\'action'), max_length=500, blank=True)
    
    # Statut
    status = models.CharField(
        _('statut'),
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
        db_index=True
    )
    
    # Email/SMS spécifique (si différent de l'utilisateur)
    recipient_email = models.EmailField(_('email destinataire'), blank=True)
    recipient_phone = models.CharField(_('téléphone destinataire'), max_length=17, blank=True)
    
    # Envoi
    sent_at = models.DateTimeField(_('envoyé le'), null=True, blank=True)
    read_at = models.DateTimeField(_('lu le'), null=True, blank=True)
    
    # Tentatives
    attempts = models.PositiveIntegerField(_('tentatives'), default=0)
    max_attempts = models.PositiveIntegerField(_('tentatives max'), default=3)
    
    # Erreur
    error_message = models.TextField(_('message d\'erreur'), blank=True)
    
    # Planification
    scheduled_at = models.DateTimeField(
        _('planifié pour'),
        null=True,
        blank=True,
        help_text=_('Date/heure d\'envoi planifié')
    )
    
    # Métadonnées
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['notification_type', 'status']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['status', 'scheduled_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.user.email} - {self.title}"
    
    @property
    def is_read(self):
        return self.status == self.READ
    
    @property
    def can_retry(self):
        return self.status == self.FAILED and self.attempts < self.max_attempts
"""
Modèle Claim pour gérer les réclamations
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Claim(models.Model):
    """Réclamation client"""
    
    # Catégories
    PAYMENT_ISSUE = 'payment_issue'
    BOOKING_ISSUE = 'booking_issue'
    SERVICE_QUALITY = 'service_quality'
    REFUND_REQUEST = 'refund_request'
    TECHNICAL_ISSUE = 'technical_issue'
    COMPLAINT = 'complaint'
    OTHER = 'other'
    
    CATEGORY_CHOICES = [
        (PAYMENT_ISSUE, _('Problème de paiement')),
        (BOOKING_ISSUE, _('Problème de réservation')),
        (SERVICE_QUALITY, _('Qualité de service')),
        (REFUND_REQUEST, _('Demande de remboursement')),
        (TECHNICAL_ISSUE, _('Problème technique')),
        (COMPLAINT, _('Plainte')),
        (OTHER, _('Autre')),
    ]
    
    # Statuts
    OPEN = 'open'
    IN_PROGRESS = 'in_progress'
    RESOLVED = 'resolved'
    CLOSED = 'closed'
    REJECTED = 'rejected'
    
    STATUS_CHOICES = [
        (OPEN, _('Ouverte')),
        (IN_PROGRESS, _('En cours')),
        (RESOLVED, _('Résolue')),
        (CLOSED, _('Fermée')),
        (REJECTED, _('Rejetée')),
    ]
    
    # Priorités
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    URGENT = 'urgent'
    
    PRIORITY_CHOICES = [
        (LOW, _('Basse')),
        (MEDIUM, _('Moyenne')),
        (HIGH, _('Haute')),
        (URGENT, _('Urgente')),
    ]
    
    # Relations
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='claims',
        verbose_name=_('utilisateur')
    )
    
    ticket = models.ForeignKey(
        'tickets.Ticket',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='claims',
        verbose_name=_('ticket')
    )
    
    trip = models.ForeignKey(
        'trips.Trip',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='claims',
        verbose_name=_('voyage')
    )
    
    assigned_to = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_claims',
        verbose_name=_('assignée à'),
        limit_choices_to={'role': 'admin'}
    )
    
    # Informations réclamation
    category = models.CharField(
        _('catégorie'),
        max_length=50,
        choices=CATEGORY_CHOICES,
        db_index=True
    )
    
    subject = models.CharField(_('sujet'), max_length=255)
    description = models.TextField(_('description'))
    
    # Pièces jointes
    attachment_1 = models.FileField(
        _('pièce jointe 1'),
        upload_to='claims/attachments/%Y/%m/',
        null=True,
        blank=True
    )
    
    attachment_2 = models.FileField(
        _('pièce jointe 2'),
        upload_to='claims/attachments/%Y/%m/',
        null=True,
        blank=True
    )
    
    attachment_3 = models.FileField(
        _('pièce jointe 3'),
        upload_to='claims/attachments/%Y/%m/',
        null=True,
        blank=True
    )
    
    # Statut et priorité
    status = models.CharField(
        _('statut'),
        max_length=20,
        choices=STATUS_CHOICES,
        default=OPEN,
        db_index=True
    )
    
    priority = models.CharField(
        _('priorité'),
        max_length=20,
        choices=PRIORITY_CHOICES,
        default=MEDIUM,
        db_index=True
    )
    
    # Réponse admin
    admin_response = models.TextField(_('réponse admin'), blank=True)
    resolution_notes = models.TextField(_('notes de résolution'), blank=True)
    
    # Dates
    created_at = models.DateTimeField(_('créée le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifiée le'), auto_now=True)
    resolved_at = models.DateTimeField(_('résolue le'), null=True, blank=True)
    closed_at = models.DateTimeField(_('fermée le'), null=True, blank=True)
    
    class Meta:
        db_table = 'claims'
        verbose_name = _('réclamation')
        verbose_name_plural = _('réclamations')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Claim #{self.pk} - {self.subject}"
    
    @property
    def is_open(self):
        return self.status in [self.OPEN, self.IN_PROGRESS]
    
    @property
    def response_time(self):
        """Calcule le temps de réponse"""
        if self.resolved_at:
            return self.resolved_at - self.created_at
        return None


class ClaimMessage(models.Model):
    """Messages dans une réclamation (conversation)"""
    
    claim = models.ForeignKey(
        Claim,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('réclamation')
    )
    
    sender = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='claim_messages',
        verbose_name=_('expéditeur')
    )
    
    message = models.TextField(_('message'))
    
    is_internal = models.BooleanField(
        _('interne'),
        default=False,
        help_text=_('Message visible uniquement par les admins')
    )
    
    attachment = models.FileField(
        _('pièce jointe'),
        upload_to='claims/messages/%Y/%m/',
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    
    class Meta:
        db_table = 'claim_messages'
        verbose_name = _('message réclamation')
        verbose_name_plural = _('messages réclamation')
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message de {self.sender.get_full_name()} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
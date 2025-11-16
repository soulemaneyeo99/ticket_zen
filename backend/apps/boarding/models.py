"""
Modèle BoardingPass pour gérer les embarquements
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class BoardingPass(models.Model):
    """Enregistrement d'embarquement (scan QR code)"""
    
    # Statuts
    VALID = 'valid'
    INVALID = 'invalid'
    ALREADY_USED = 'already_used'
    EXPIRED = 'expired'
    WRONG_TRIP = 'wrong_trip'
    
    STATUS_CHOICES = [
        (VALID, _('Valide')),
        (INVALID, _('Invalide')),
        (ALREADY_USED, _('Déjà utilisé')),
        (EXPIRED, _('Expiré')),
        (WRONG_TRIP, _('Mauvais voyage')),
    ]
    
    # Relations
    ticket = models.ForeignKey(
        'tickets.Ticket',
        on_delete=models.CASCADE,
        related_name='boarding_passes',
        verbose_name=_('ticket')
    )
    
    trip = models.ForeignKey(
        'trips.Trip',
        on_delete=models.CASCADE,
        related_name='boarding_passes',
        verbose_name=_('voyage')
    )
    
    boarding_agent = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='boarded_passes',
        verbose_name=_('embarqueur'),
        limit_choices_to={'role': 'embarqueur'}
    )
    
    # Informations scan
    scan_status = models.CharField(
        _('statut scan'),
        max_length=20,
        choices=STATUS_CHOICES,
        default=VALID,
        db_index=True
    )
    
    scanned_at = models.DateTimeField(_('scanné le'), auto_now_add=True, db_index=True)
    
    # Localisation
    latitude = models.DecimalField(
        _('latitude'),
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    
    longitude = models.DecimalField(
        _('longitude'),
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    
    # Métadonnées
    device_info = models.JSONField(
        _('info appareil'),
        default=dict,
        blank=True,
        help_text=_('Informations sur l\'appareil mobile utilisé')
    )
    
    is_offline_scan = models.BooleanField(
        _('scan hors ligne'),
        default=False,
        help_text=_('Scan effectué en mode hors ligne')
    )
    
    synced_at = models.DateTimeField(
        _('synchronisé le'),
        null=True,
        blank=True,
        help_text=_('Date de synchronisation si scan offline')
    )
    
    notes = models.TextField(_('notes'), blank=True)
    
    class Meta:
        db_table = 'boarding_passes'
        verbose_name = _('pass embarquement')
        verbose_name_plural = _('passes embarquement')
        ordering = ['-scanned_at']
        indexes = [
            models.Index(fields=['ticket', 'trip']),
            models.Index(fields=['boarding_agent', 'scanned_at']),
            models.Index(fields=['scan_status']),
            models.Index(fields=['is_offline_scan', 'synced_at']),
        ]
    
    def __str__(self):
        return f"Boarding {self.ticket.ticket_number} - {self.scanned_at.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def is_valid_scan(self):
        return self.scan_status == self.VALID
"""
Modèle Ticket pour gérer les réservations
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class Ticket(models.Model):
    """Ticket de voyage"""
    
    # Statuts
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    CANCELLED = 'cancelled'
    USED = 'used'
    EXPIRED = 'expired'
    REFUNDED = 'refunded'
    
    STATUS_CHOICES = [
        (PENDING, _('En attente')),
        (CONFIRMED, _('Confirmé')),
        (CANCELLED, _('Annulé')),
        (USED, _('Utilisé')),
        (EXPIRED, _('Expiré')),
        (REFUNDED, _('Remboursé')),
    ]
    
    # Identifiants uniques
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_number = models.CharField(
        _('numéro de ticket'),
        max_length=20,
        unique=True,
        db_index=True,
        editable=False
    )
    
    # Relations
    trip = models.ForeignKey(
        'trips.Trip',
        on_delete=models.PROTECT,
        related_name='tickets',
        verbose_name=_('voyage')
    )
    
    passenger = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='tickets',
        verbose_name=_('passager'),
        limit_choices_to={'role': 'voyageur'}
    )
    
    # Informations passager (peut différer de l'utilisateur)
    passenger_first_name = models.CharField(_('prénom passager'), max_length=150)
    passenger_last_name = models.CharField(_('nom passager'), max_length=150)
    passenger_phone = models.CharField(_('téléphone passager'), max_length=17)
    passenger_email = models.EmailField(_('email passager'))
    passenger_id_number = models.CharField(
        _('numéro CNI/Passport'),
        max_length=50,
        blank=True
    )
    
    # Siège
    seat_number = models.CharField(_('numéro de siège'), max_length=10, db_index=True)
    
    # Prix
    price = models.DecimalField(
        _('prix'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    platform_fee = models.DecimalField(
        _('frais plateforme'),
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    
    total_amount = models.DecimalField(
        _('montant total'),
        max_digits=10,
        decimal_places=2
    )
    
    # Statut
    status = models.CharField(
        _('statut'),
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
        db_index=True
    )
    
    # Paiement
    payment = models.OneToOneField(
        'payments.Payment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ticket',
        verbose_name=_('paiement')
    )
    
    is_paid = models.BooleanField(_('payé'), default=False, db_index=True)
    
    # QR Code
    qr_code = models.TextField(_('QR code'), blank=True)
    qr_code_image = models.ImageField(
        _('image QR code'),
        upload_to='tickets/qr_codes/%Y/%m/',
        null=True,
        blank=True
    )
    
    # Embarquement
    boarding_time = models.DateTimeField(_('heure embarquement'), null=True, blank=True)
    boarded_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='boarded_tickets',
        verbose_name=_('embarqué par'),
        limit_choices_to={'role': 'embarqueur'}
    )
    
    # Annulation
    cancelled_at = models.DateTimeField(_('annulé le'), null=True, blank=True)
    cancellation_reason = models.TextField(_('raison annulation'), blank=True)
    refund_amount = models.DecimalField(
        _('montant remboursé'),
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    
    # Notes
    notes = models.TextField(_('notes'), blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    confirmed_at = models.DateTimeField(_('confirmé le'), null=True, blank=True)
    
    class Meta:
        db_table = 'tickets'
        verbose_name = _('ticket')
        verbose_name_plural = _('tickets')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ticket_number']),
            models.Index(fields=['trip', 'status']),
            models.Index(fields=['passenger', 'status']),
            models.Index(fields=['status', 'is_paid']),
            models.Index(fields=['trip', 'seat_number']),
        ]
        unique_together = [
            ['trip', 'seat_number'],
        ]
    
    def __str__(self):
        return f"Ticket {self.ticket_number} - {self.passenger_first_name} {self.passenger_last_name}"
    
    def save(self, *args, **kwargs):
        # Générer le numéro de ticket si nouveau
        if not self.ticket_number:
            self.ticket_number = self.generate_ticket_number()
        
        # Calculer le montant total
        self.total_amount = self.price + self.platform_fee
        
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_ticket_number():
        """Génère un numéro de ticket unique"""
        import random
        import string
        from django.utils import timezone
        
        date_part = timezone.now().strftime('%Y%m%d')
        random_part = ''.join(random.choices(string.digits, k=6))
        return f"TZ{date_part}{random_part}"
    
    @property
    def is_valid(self):
        """Vérifie si le ticket est valide"""
        return (
            self.status == self.CONFIRMED and
            self.is_paid and
            not self.trip.is_past
        )
    
    @property
    def can_be_cancelled(self):
        """Vérifie si le ticket peut être annulé"""
        from django.utils import timezone
        
        if self.status != self.CONFIRMED:
            return False
        
        if not self.trip.allows_cancellation:
            return False
        
        # Vérifier le délai d'annulation
        deadline = self.trip.departure_datetime - timezone.timedelta(
            hours=self.trip.cancellation_deadline_hours
        )
        
        return timezone.now() < deadline
    
    @property
    def passenger_full_name(self):
        return f"{self.passenger_first_name} {self.passenger_last_name}"
"""
Modèle Payment pour gérer les paiements
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class Payment(models.Model):
    """Paiement effectué par un voyageur"""
    
    # Méthodes de paiement
    ORANGE_MONEY = 'orange_money'
    MTN_MONEY = 'mtn_money'
    MOOV_MONEY = 'moov_money'
    WAVE = 'wave'
    VISA = 'visa'
    MASTERCARD = 'mastercard'
    
    PAYMENT_METHOD_CHOICES = [
        (ORANGE_MONEY, _('Orange Money')),
        (MTN_MONEY, _('MTN Money')),
        (MOOV_MONEY, _('Moov Money')),
        (WAVE, _('Wave')),
        (VISA, _('Visa')),
        (MASTERCARD, _('Mastercard')),
    ]
    
    # Statuts
    PENDING = 'pending'
    PROCESSING = 'processing'
    SUCCESS = 'success'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
    REFUNDED = 'refunded'
    
    STATUS_CHOICES = [
        (PENDING, _('En attente')),
        (PROCESSING, _('En cours')),
        (SUCCESS, _('Réussi')),
        (FAILED, _('Échoué')),
        (CANCELLED, _('Annulé')),
        (REFUNDED, _('Remboursé')),
    ]
    
    # Identifiants
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_id = models.CharField(
        _('ID transaction'),
        max_length=100,
        unique=True,
        db_index=True,
        editable=False
    )
    
    # Relations
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('utilisateur')
    )
    
    trip = models.ForeignKey(
        'trips.Trip',
        on_delete=models.PROTECT,
        related_name='payments',
        verbose_name=_('voyage')
    )
    
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.PROTECT,
        related_name='payments',
        verbose_name=_('compagnie')
    )
    
    # Montants
    amount = models.DecimalField(
        _('montant'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    platform_commission = models.DecimalField(
        _('commission plateforme'),
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    
    company_amount = models.DecimalField(
        _('montant compagnie'),
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    
    # Méthode de paiement
    payment_method = models.CharField(
        _('méthode de paiement'),
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        db_index=True
    )
    
    # Informations paiement
    phone_number = models.CharField(
        _('numéro de téléphone'),
        max_length=17,
        blank=True,
        help_text=_('Pour mobile money')
    )
    
    # Statut
    status = models.CharField(
        _('statut'),
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
        db_index=True
    )
    
    # Données provider (CinetPay)
    provider_transaction_id = models.CharField(
        _('ID transaction provider'),
        max_length=200,
        blank=True,
        db_index=True
    )
    
    provider_response = models.JSONField(
        _('réponse provider'),
        default=dict,
        blank=True
    )
    
    payment_url = models.URLField(
        _('URL de paiement'),
        max_length=500,
        blank=True
    )
    
    # Remboursement
    refund_transaction_id = models.CharField(
        _('ID transaction remboursement'),
        max_length=100,
        blank=True
    )
    
    refund_amount = models.DecimalField(
        _('montant remboursé'),
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    
    refund_reason = models.TextField(_('raison remboursement'), blank=True)
    refunded_at = models.DateTimeField(_('remboursé le'), null=True, blank=True)
    
    # Métadonnées
    ip_address = models.GenericIPAddressField(_('adresse IP'), null=True, blank=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    completed_at = models.DateTimeField(_('complété le'), null=True, blank=True)
    
    # Notes
    notes = models.TextField(_('notes'), blank=True)
    
    class Meta:
        db_table = 'payments'
        verbose_name = _('paiement')
        verbose_name_plural = _('paiements')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['company', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['provider_transaction_id']),
            models.Index(fields=['payment_method', 'status']),
        ]
    
    def __str__(self):
        return f"Payment {self.transaction_id} - {self.amount} XOF"
    
    def save(self, *args, **kwargs):
        # Générer transaction_id si nouveau
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        
        # Calculer les montants
        if not self.pk:
            self.platform_commission = self.company.calculate_commission(self.amount)
            self.company_amount = self.amount - self.platform_commission
        
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_transaction_id():
        """Génère un ID de transaction unique"""
        import random
        import string
        from django.utils import timezone
        
        date_part = timezone.now().strftime('%Y%m%d%H%M%S')
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"PAY{date_part}{random_part}"
    
    @property
    def is_successful(self):
        return self.status == self.SUCCESS
    
    @property
    def is_pending(self):
        return self.status in [self.PENDING, self.PROCESSING]
    
    @property
    def can_be_refunded(self):
        return self.status == self.SUCCESS and self.refund_amount == 0
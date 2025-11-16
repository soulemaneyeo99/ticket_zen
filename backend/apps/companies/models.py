"""
Modèle Company pour gérer les compagnies de transport
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class Company(models.Model):
    """Compagnie de transport"""
    
    # Statuts de validation
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    SUSPENDED = 'suspended'
    
    STATUS_CHOICES = [
        (PENDING, _('En attente')),
        (APPROVED, _('Approuvée')),
        (REJECTED, _('Rejetée')),
        (SUSPENDED, _('Suspendue')),
    ]
    
    # Informations de base
    name = models.CharField(_('nom'), max_length=255, unique=True, db_index=True)
    slug = models.SlugField(_('slug'), max_length=255, unique=True)
    
    # Informations légales
    registration_number = models.CharField(
        _('numéro d\'enregistrement'),
        max_length=100,
        unique=True,
        db_index=True
    )
    tax_id = models.CharField(
        _('identifiant fiscal'),
        max_length=100,
        unique=True,
        blank=True,
        null=True
    )
    
    # Contact
    email = models.EmailField(_('email'), unique=True)
    phone_number = models.CharField(_('téléphone'), max_length=17)
    address = models.TextField(_('adresse'))
    city = models.CharField(_('ville'), max_length=100, db_index=True)
    country = models.CharField(_('pays'), max_length=100, default='Côte d\'Ivoire')
    
    # Présentation
    description = models.TextField(_('description'), blank=True)
    logo = models.ImageField(
        _('logo'),
        upload_to='companies/logos/%Y/%m/',
        null=True,
        blank=True
    )
    
    # Documents légaux
    license_document = models.FileField(
        _('licence de transport'),
        upload_to='companies/documents/%Y/%m/',
        null=True,
        blank=True
    )
    insurance_document = models.FileField(
        _('assurance'),
        upload_to='companies/documents/%Y/%m/',
        null=True,
        blank=True
    )
    
    # Statut et validation
    status = models.CharField(
        _('statut'),
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
        db_index=True
    )
    is_active = models.BooleanField(_('active'), default=True, db_index=True)
    
    # Notes admin
    admin_notes = models.TextField(
        _('notes admin'),
        blank=True,
        help_text=_('Notes internes visibles uniquement par les admins')
    )
    
    # Validation
    validated_at = models.DateTimeField(_('validée le'), null=True, blank=True)
    validated_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validated_companies',
        verbose_name=_('validée par')
    )
    
    # Commission
    commission_rate = models.DecimalField(
        _('taux de commission'),
        max_digits=5,
        decimal_places=2,
        default=5.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Pourcentage de commission (%)'),
    )
    
    # Statistiques
    total_trips = models.PositiveIntegerField(_('total voyages'), default=0)
    total_tickets_sold = models.PositiveIntegerField(_('total tickets vendus'), default=0)
    total_revenue = models.DecimalField(
        _('revenu total'),
        max_digits=15,
        decimal_places=2,
        default=0.00
    )
    
    # Métadonnées
    created_at = models.DateTimeField(_('créée le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifiée le'), auto_now=True)
    
    class Meta:
        db_table = 'companies'
        verbose_name = _('compagnie')
        verbose_name_plural = _('compagnies')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'is_active']),
            models.Index(fields=['city', 'is_active']),
            models.Index(fields=['slug']),
            models.Index(fields=['registration_number']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def is_approved(self):
        return self.status == self.APPROVED and self.is_active
    
    def calculate_commission(self, amount):
        """Calcule le montant de commission"""
        return (amount * self.commission_rate) / 100
    
    def increment_stats(self, trip_count=0, ticket_count=0, revenue=0):
        """Incrémente les statistiques"""
        self.total_trips += trip_count
        self.total_tickets_sold += ticket_count
        self.total_revenue += revenue
        self.save(update_fields=['total_trips', 'total_tickets_sold', 'total_revenue'])
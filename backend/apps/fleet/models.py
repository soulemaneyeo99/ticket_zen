"""
Modèle Vehicle pour gérer la flotte de véhicules
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator


class Vehicle(models.Model):
    """Véhicule d'une compagnie"""
    
    # Types de véhicules
    BUS = 'bus'
    MINIBUS = 'minibus'
    VAN = 'van'
    CAR = 'car'
    
    VEHICLE_TYPE_CHOICES = [
        (BUS, _('Bus')),
        (MINIBUS, _('Minibus')),
        (VAN, _('Van')),
        (CAR, _('Voiture')),
    ]
    
    # Statuts
    ACTIVE = 'active'
    MAINTENANCE = 'maintenance'
    INACTIVE = 'inactive'
    
    STATUS_CHOICES = [
        (ACTIVE, _('Actif')),
        (MAINTENANCE, _('En maintenance')),
        (INACTIVE, _('Inactif')),
    ]
    
    # Relation avec compagnie
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='vehicles',
        verbose_name=_('compagnie')
    )
    
    # Informations du véhicule
    vehicle_type = models.CharField(
        _('type de véhicule'),
        max_length=20,
        choices=VEHICLE_TYPE_CHOICES,
        default=BUS
    )
    
    registration_number = models.CharField(
        _('numéro d\'immatriculation'),
        max_length=50,
        unique=True,
        db_index=True
    )
    
    brand = models.CharField(_('marque'), max_length=100)
    model = models.CharField(_('modèle'), max_length=100)
    year = models.PositiveIntegerField(
        _('année'),
        validators=[MinValueValidator(1990)]
    )
    
    color = models.CharField(_('couleur'), max_length=50, blank=True)
    
    # Capacité
    total_seats = models.PositiveIntegerField(
        _('nombre de places'),
        validators=[MinValueValidator(1)]
    )
    
    seat_configuration = models.JSONField(
        _('configuration des sièges'),
        default=dict,
        blank=True,
        help_text=_('Configuration JSON des sièges avec numéros et types')
    )
    
    # Équipements
    has_ac = models.BooleanField(_('climatisation'), default=True)
    has_wifi = models.BooleanField(_('WiFi'), default=False)
    has_tv = models.BooleanField(_('TV'), default=False)
    has_usb_ports = models.BooleanField(_('ports USB'), default=False)
    has_toilet = models.BooleanField(_('toilettes'), default=False)
    
    # Statut
    status = models.CharField(
        _('statut'),
        max_length=20,
        choices=STATUS_CHOICES,
        default=ACTIVE,
        db_index=True
    )
    
    is_active = models.BooleanField(_('actif'), default=True)
    
    # Photos
    photo_main = models.ImageField(
        _('photo principale'),
        upload_to='vehicles/photos/%Y/%m/',
        null=True,
        blank=True
    )
    
    photo_interior = models.ImageField(
        _('photo intérieur'),
        upload_to='vehicles/photos/%Y/%m/',
        null=True,
        blank=True
    )
    
    # Documents
    insurance_expiry = models.DateField(_('expiration assurance'), null=True, blank=True)
    technical_inspection_expiry = models.DateField(
        _('expiration visite technique'),
        null=True,
        blank=True
    )
    
    # Maintenance
    last_maintenance_date = models.DateField(
        _('dernière maintenance'),
        null=True,
        blank=True
    )
    next_maintenance_date = models.DateField(
        _('prochaine maintenance'),
        null=True,
        blank=True
    )
    
    maintenance_notes = models.TextField(_('notes de maintenance'), blank=True)
    
    # Statistiques
    total_trips = models.PositiveIntegerField(_('total voyages'), default=0)
    total_km = models.DecimalField(
        _('kilométrage total'),
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    
    # Métadonnées
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    
    class Meta:
        db_table = 'vehicles'
        verbose_name = _('véhicule')
        verbose_name_plural = _('véhicules')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', 'status']),
            models.Index(fields=['registration_number']),
            models.Index(fields=['vehicle_type', 'status']),
        ]
    
    def __str__(self):
        return f"{self.brand} {self.model} - {self.registration_number}"
    
    @property
    def is_available(self):
        """Vérifie si le véhicule est disponible"""
        return self.status == self.ACTIVE and self.is_active
    
    def get_seat_map(self):
        """Retourne la configuration des sièges"""
        if self.seat_configuration:
            return self.seat_configuration
        
        # Configuration par défaut si non définie
        return {
            'rows': self.total_seats // 4,
            'columns': 4,
            'seats': [{'number': i + 1, 'type': 'standard'} for i in range(self.total_seats)]
        }
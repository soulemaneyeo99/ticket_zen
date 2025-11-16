"""
Modèle Trip pour gérer les voyages
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal


class City(models.Model):
    """Villes desservies"""
    
    name = models.CharField(_('nom'), max_length=100, unique=True, db_index=True)
    slug = models.SlugField(_('slug'), max_length=100, unique=True)
    country = models.CharField(_('pays'), max_length=100, default='Côte d\'Ivoire')
    
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
    
    is_active = models.BooleanField(_('active'), default=True)
    
    created_at = models.DateTimeField(_('créée le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifiée le'), auto_now=True)
    
    class Meta:
        db_table = 'cities'
        verbose_name = _('ville')
        verbose_name_plural = _('villes')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Trip(models.Model):
    """Voyage proposé par une compagnie"""
    
    # Statuts
    SCHEDULED = 'scheduled'
    BOARDING = 'boarding'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (SCHEDULED, _('Programmé')),
        (BOARDING, _('Embarquement')),
        (IN_PROGRESS, _('En cours')),
        (COMPLETED, _('Terminé')),
        (CANCELLED, _('Annulé')),
    ]
    
    # Relations
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='trips',
        verbose_name=_('compagnie')
    )
    
    vehicle = models.ForeignKey(
        'fleet.Vehicle',
        on_delete=models.PROTECT,
        related_name='trips',
        verbose_name=_('véhicule')
    )
    
    # Trajet
    departure_city = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        related_name='departures',
        verbose_name=_('ville de départ')
    )
    
    arrival_city = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        related_name='arrivals',
        verbose_name=_('ville d\'arrivée')
    )
    
    departure_location = models.CharField(
        _('lieu de départ'),
        max_length=255,
        help_text=_('Gare routière, adresse précise')
    )
    
    arrival_location = models.CharField(
        _('lieu d\'arrivée'),
        max_length=255,
        help_text=_('Gare routière, adresse précise')
    )
    
    # Date et heure
    departure_datetime = models.DateTimeField(_('date/heure de départ'), db_index=True)
    estimated_arrival_datetime = models.DateTimeField(_('arrivée estimée'))
    actual_departure_datetime = models.DateTimeField(_('départ réel'), null=True, blank=True)
    actual_arrival_datetime = models.DateTimeField(_('arrivée réelle'), null=True, blank=True)
    
    # Durée estimée (en minutes)
    estimated_duration = models.PositiveIntegerField(
        _('durée estimée (minutes)'),
        validators=[MinValueValidator(1)]
    )
    
    # Distance (en km)
    distance_km = models.DecimalField(
        _('distance (km)'),
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    # Prix
    base_price = models.DecimalField(
        _('prix de base'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    # Places
    total_seats = models.PositiveIntegerField(_('places totales'))
    available_seats = models.PositiveIntegerField(_('places disponibles'))
    reserved_seats = models.PositiveIntegerField(_('places réservées'), default=0)
    
    # Statut
    status = models.CharField(
        _('statut'),
        max_length=20,
        choices=STATUS_CHOICES,
        default=SCHEDULED,
        db_index=True
    )
    
    is_active = models.BooleanField(_('actif'), default=True, db_index=True)
    is_recurring = models.BooleanField(_('récurrent'), default=False)
    
    # Options supplémentaires
    allows_cancellation = models.BooleanField(_('annulation autorisée'), default=True)
    cancellation_deadline_hours = models.PositiveIntegerField(
        _('délai annulation (heures)'),
        default=24,
        help_text=_('Nombre d\'heures avant le départ pour annuler')
    )
    
    # Notes
    notes = models.TextField(_('notes'), blank=True)
    driver_notes = models.TextField(_('notes chauffeur'), blank=True)
    
    # Embarqueurs assignés
    boarding_agents = models.ManyToManyField(
        'users.User',
        related_name='assigned_trips',
        verbose_name=_('embarqueurs'),
        blank=True,
        limit_choices_to={'role': 'embarqueur'}
    )
    
    # Statistiques
    total_revenue = models.DecimalField(
        _('revenu total'),
        max_digits=12,
        decimal_places=2,
        default=0.00
    )
    
    commission_amount = models.DecimalField(
        _('montant commission'),
        max_digits=12,
        decimal_places=2,
        default=0.00
    )
    
    # Métadonnées
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_trips',
        verbose_name=_('créé par')
    )
    
    class Meta:
        db_table = 'trips'
        verbose_name = _('voyage')
        verbose_name_plural = _('voyages')
        ordering = ['departure_datetime']
        indexes = [
            models.Index(fields=['departure_city', 'arrival_city', 'departure_datetime']),
            models.Index(fields=['company', 'status']),
            models.Index(fields=['departure_datetime', 'status']),
            models.Index(fields=['status', 'is_active']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(available_seats__lte=models.F('total_seats')),
                name='available_seats_not_exceed_total'
            ),
        ]
    
    def __str__(self):
        return f"{self.departure_city} → {self.arrival_city} - {self.departure_datetime.strftime('%d/%m/%Y %H:%M')}"
    
    def save(self, *args, **kwargs):
        # S'assurer que total_seats correspond au véhicule
        if not self.pk and self.vehicle:
            self.total_seats = self.vehicle.total_seats
            self.available_seats = self.total_seats
        super().save(*args, **kwargs)
    
    @property
    def is_full(self):
        """Vérifie si le voyage est complet"""
        return self.available_seats == 0
    
    @property
    def is_past(self):
        """Vérifie si le voyage est passé"""
        return self.departure_datetime < timezone.now()
    
    @property
    def can_be_booked(self):
        """Vérifie si le voyage peut être réservé"""
        return (
            self.is_active and
            self.status == self.SCHEDULED and
            self.available_seats > 0 and
            not self.is_past
        )
    
    @property
    def occupancy_rate(self):
        """Taux d'occupation en pourcentage"""
        if self.total_seats == 0:
            return 0
        return ((self.total_seats - self.available_seats) / self.total_seats) * 100
    
    def reserve_seats(self, count=1):
        """Réserve des places"""
        if self.available_seats >= count:
            self.available_seats -= count
            self.reserved_seats += count
            self.save(update_fields=['available_seats', 'reserved_seats'])
            return True
        return False
    
    def release_seats(self, count=1):
        """Libère des places"""
        self.available_seats += count
        self.reserved_seats = max(0, self.reserved_seats - count)
        self.save(update_fields=['available_seats', 'reserved_seats'])
    
    def calculate_commission(self):
        """Calcule la commission de la plateforme"""
        return self.company.calculate_commission(self.total_revenue)
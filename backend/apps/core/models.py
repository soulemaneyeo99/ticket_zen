"""
Modèles pour configuration et paramètres de la plateforme
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.cache import cache


class PlatformSettings(models.Model):
    """Paramètres globaux de la plateforme (singleton)"""
    
    # Commissions
    default_commission_rate = models.DecimalField(
        _('taux de commission par défaut'),
        max_digits=5,
        decimal_places=2,
        default=5.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Pourcentage de commission (%)'),
    )
    
    # Délais
    ticket_cancellation_deadline_hours = models.PositiveIntegerField(
        _('délai annulation ticket (heures)'),
        default=24,
        help_text=_('Nombre d\'heures avant le départ pour annuler un ticket')
    )
    
    # Notifications
    send_email_notifications = models.BooleanField(
        _('envoyer notifications email'),
        default=True
    )
    
    send_sms_notifications = models.BooleanField(
        _('envoyer notifications SMS'),
        default=True
    )
    
    trip_reminder_hours_before = models.PositiveIntegerField(
        _('rappel voyage (heures avant)'),
        default=24,
        help_text=_('Envoyer un rappel X heures avant le départ')
    )
    
    # Paiements
    payment_timeout_minutes = models.PositiveIntegerField(
        _('timeout paiement (minutes)'),
        default=15,
        help_text=_('Durée de validité d\'une transaction de paiement')
    )
    
    min_ticket_price = models.DecimalField(
        _('prix minimum ticket'),
        max_digits=10,
        decimal_places=2,
        default=500.00,
        validators=[MinValueValidator(0)]
    )
    
    max_ticket_price = models.DecimalField(
        _('prix maximum ticket'),
        max_digits=10,
        decimal_places=2,
        default=100000.00,
        validators=[MinValueValidator(0)]
    )
    
    # QR Code
    qr_code_expiration_hours = models.PositiveIntegerField(
        _('expiration QR code (heures)'),
        default=24,
        help_text=_('Durée de validité du QR code après le départ')
    )
    
    # Réservations
    max_tickets_per_booking = models.PositiveIntegerField(
        _('tickets max par réservation'),
        default=10
    )
    
    allow_overbooking = models.BooleanField(
        _('autoriser surréservation'),
        default=False
    )
    
    overbooking_percentage = models.DecimalField(
        _('pourcentage surréservation'),
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(50)]
    )
    
    # Maintenance
    maintenance_mode = models.BooleanField(
        _('mode maintenance'),
        default=False
    )
    
    maintenance_message = models.TextField(
        _('message maintenance'),
        blank=True,
        default='La plateforme est actuellement en maintenance. Veuillez réessayer plus tard.'
    )
    
    # Contact
    support_email = models.EmailField(
        _('email support'),
        default='support@ticketzen.com'
    )
    
    support_phone = models.CharField(
        _('téléphone support'),
        max_length=17,
        default='+225XXXXXXXXXX'
    )
    
    # Métadonnées
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    updated_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='settings_updates',
        verbose_name=_('modifié par')
    )
    
    class Meta:
        db_table = 'platform_settings'
        verbose_name = _('paramètres plateforme')
        verbose_name_plural = _('paramètres plateforme')
    
    def __str__(self):
        return "Paramètres de la plateforme"
    
    def save(self, *args, **kwargs):
        self.pk = 1  # Forcer singleton
        super().save(*args, **kwargs)
        # Invalider le cache
        cache.delete('platform_settings')
    
    @classmethod
    def load(cls):
        """Charge les paramètres (avec cache)"""
        settings = cache.get('platform_settings')
        if settings is None:
            settings, created = cls.objects.get_or_create(pk=1)
            cache.set('platform_settings', settings, 3600)  # Cache 1 heure
        return settings


class FAQ(models.Model):
    """Questions fréquentes"""
    
    # Catégories
    GENERAL = 'general'
    BOOKING = 'booking'
    PAYMENT = 'payment'
    CANCELLATION = 'cancellation'
    ACCOUNT = 'account'
    
    CATEGORY_CHOICES = [
        (GENERAL, _('Général')),
        (BOOKING, _('Réservation')),
        (PAYMENT, _('Paiement')),
        (CANCELLATION, _('Annulation')),
        (ACCOUNT, _('Compte')),
    ]
    
    category = models.CharField(
        _('catégorie'),
        max_length=50,
        choices=CATEGORY_CHOICES,
        db_index=True
    )
    
    question = models.TextField(_('question'))
    answer = models.TextField(_('réponse'))
    
    order = models.PositiveIntegerField(_('ordre'), default=0)
    
    is_active = models.BooleanField(_('active'), default=True)
    
    views = models.PositiveIntegerField(_('vues'), default=0)
    
    created_at = models.DateTimeField(_('créée le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifiée le'), auto_now=True)
    
    class Meta:
        db_table = 'faqs'
        verbose_name = _('FAQ')
        verbose_name_plural = _('FAQs')
        ordering = ['category', 'order', '-views']
    
    def __str__(self):
        return self.question[:100]


class Banner(models.Model):
    """Bannières promotionnelles"""
    
    title = models.CharField(_('titre'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    
    image = models.ImageField(
        _('image'),
        upload_to='banners/%Y/%m/'
    )
    
    link_url = models.URLField(_('URL du lien'), max_length=500, blank=True)
    
    # Affichage
    is_active = models.BooleanField(_('active'), default=True)
    
    start_date = models.DateTimeField(_('date début'))
    end_date = models.DateTimeField(_('date fin'))
    
    order = models.PositiveIntegerField(_('ordre'), default=0)
    
    # Ciblage
    target_role = models.CharField(
        _('rôle ciblé'),
        max_length=20,
        blank=True,
        help_text=_('Laisser vide pour tous les utilisateurs')
    )
    
    # Statistiques
    views = models.PositiveIntegerField(_('vues'), default=0)
    clicks = models.PositiveIntegerField(_('clics'), default=0)
    
    created_at = models.DateTimeField(_('créée le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifiée le'), auto_now=True)
    
    class Meta:
        db_table = 'banners'
        verbose_name = _('bannière')
        verbose_name_plural = _('bannières')
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def is_visible(self):
        """Vérifie si la bannière est actuellement visible"""
        from django.utils import timezone
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date
    
    @property
    def click_through_rate(self):
        """Calcule le taux de clic"""
        if self.views == 0:
            return 0
        return (self.clicks / self.views) * 100
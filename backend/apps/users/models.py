"""
Modèle User avec gestion des 4 rôles : voyageur, compagnie, embarqueur, admin
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


class UserManager(BaseUserManager):
    """Manager custom pour User"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Créer un utilisateur normal"""
        if not email:
            raise ValueError(_('L\'email est obligatoire'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Créer un superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.ADMIN)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser doit avoir is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser doit avoir is_superuser=True'))
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Modèle User personnalisé avec 4 rôles"""
    
    # Rôles disponibles
    VOYAGEUR = 'voyageur'
    COMPAGNIE = 'compagnie'
    EMBARQUEUR = 'embarqueur'
    ADMIN = 'admin'
    
    ROLE_CHOICES = [
        (VOYAGEUR, _('Voyageur')),
        (COMPAGNIE, _('Compagnie')),
        (EMBARQUEUR, _('Embarqueur')),
        (ADMIN, _('Administrateur')),
    ]
    
    # Remplacer username par email
    username = None
    email = models.EmailField(_('email'), unique=True, db_index=True)
    
    # Informations personnelles
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Le numéro de téléphone doit être au format: '+225XXXXXXXXX'")
    )
    phone_number = models.CharField(
        _('téléphone'),
        validators=[phone_regex],
        max_length=17,
        unique=True,
        db_index=True
    )
    
    first_name = models.CharField(_('prénom'), max_length=150)
    last_name = models.CharField(_('nom'), max_length=150)
    
    # Rôle et statut
    role = models.CharField(
        _('rôle'),
        max_length=20,
        choices=ROLE_CHOICES,
        default=VOYAGEUR,
        db_index=True
    )
    
    is_active = models.BooleanField(_('actif'), default=True)
    is_verified = models.BooleanField(_('vérifié'), default=False)
    
    # Relation avec compagnie (pour embarqueurs et compagnies)
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name=_('compagnie')
    )
    
    # Avatar optionnel
    avatar = models.ImageField(
        _('avatar'),
        upload_to='avatars/%Y/%m/',
        null=True,
        blank=True
    )
    
    # Métadonnées
    created_at = models.DateTimeField(_('créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('modifié le'), auto_now=True)
    last_login_ip = models.GenericIPAddressField(_('dernière IP'), null=True, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']
    
    class Meta:
        db_table = 'users'
        verbose_name = _('utilisateur')
        verbose_name_plural = _('utilisateurs')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'is_active']),
            models.Index(fields=['role', 'is_active']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['company', 'role']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        """Retourne le nom complet"""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def is_voyageur(self):
        return self.role == self.VOYAGEUR
    
    @property
    def is_compagnie(self):
        return self.role == self.COMPAGNIE
    
    @property
    def is_embarqueur(self):
        return self.role == self.EMBARQUEUR
    
    @property
    def is_admin_global(self):
        return self.role == self.ADMIN
"""
Validateurs personnalisés
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re


def validate_phone_number(value):
    """Valider un numéro de téléphone"""
    pattern = r'^\+?[1-9]\d{1,14}$'
    if not re.match(pattern, value):
        raise ValidationError(
            _('Numéro de téléphone invalide. Format attendu: +225XXXXXXXXX'),
            code='invalid_phone'
        )


def validate_seat_number(value):
    """Valider un numéro de siège"""
    pattern = r'^[A-Z]\d{1,2}$'
    if not re.match(pattern, value):
        raise ValidationError(
            _('Numéro de siège invalide. Format attendu: A1, B12, etc.'),
            code='invalid_seat'
        )


def validate_positive_amount(value):
    """Valider qu'un montant est positif"""
    if value <= 0:
        raise ValidationError(
            _('Le montant doit être supérieur à 0'),
            code='invalid_amount'
        )


def validate_future_datetime(value):
    """Valider qu'une date est dans le futur"""
    from django.utils import timezone
    
    if value <= timezone.now():
        raise ValidationError(
            _('La date doit être dans le futur'),
            code='invalid_datetime'
        )


def validate_commission_rate(value):
    """Valider un taux de commission"""
    if not (0 <= value <= 100):
        raise ValidationError(
            _('Le taux de commission doit être entre 0 et 100'),
            code='invalid_commission'
        )


def validate_file_size(value, max_size_mb=5):
    """Valider la taille d'un fichier"""
    if value.size > max_size_mb * 1024 * 1024:
        raise ValidationError(
            _(f'La taille du fichier ne doit pas dépasser {max_size_mb} MB'),
            code='file_too_large'
        )


def validate_image_file(value):
    """Valider qu'un fichier est une image"""
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    import os
    ext = os.path.splitext(value.name)[1].lower()
    
    if ext not in valid_extensions:
        raise ValidationError(
            _('Format d\'image non supporté. Formats acceptés: JPG, PNG, GIF'),
            code='invalid_image_format'
        )
    
    validate_file_size(value, max_size_mb=5)


def validate_document_file(value):
    """Valider qu'un fichier est un document"""
    valid_extensions = ['.pdf', '.doc', '.docx']
    import os
    ext = os.path.splitext(value.name)[1].lower()
    
    if ext not in valid_extensions:
        raise ValidationError(
            _('Format de document non supporté. Formats acceptés: PDF, DOC, DOCX'),
            code='invalid_document_format'
        )
    
    validate_file_size(value, max_size_mb=10)
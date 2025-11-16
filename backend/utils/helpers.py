"""
Fonctions helper utilitaires
"""
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import random
import string


def generate_random_string(length=10, include_digits=True, include_special=False):
    """Générer une chaîne aléatoire"""
    chars = string.ascii_letters
    if include_digits:
        chars += string.digits
    if include_special:
        chars += string.punctuation
    
    return ''.join(random.choices(chars, k=length))


def generate_unique_code(prefix='', length=8):
    """Générer un code unique avec préfixe"""
    random_part = generate_random_string(length, include_digits=True, include_special=False).upper()
    return f"{prefix}{random_part}" if prefix else random_part


def calculate_percentage(value, total):
    """Calculer un pourcentage"""
    if total == 0:
        return Decimal('0.00')
    return Decimal(value) / Decimal(total) * Decimal('100.00')


def format_currency(amount, currency='FCFA'):
    """Formater un montant en devise"""
    return f"{amount:,.0f} {currency}"


def get_datetime_range(period='today'):
    """
    Obtenir une plage de dates/heures
    
    Args:
        period: 'today', 'yesterday', 'week', 'month', 'year'
    
    Returns:
        tuple: (start_datetime, end_datetime)
    """
    now = timezone.now()
    
    if period == 'today':
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    elif period == 'yesterday':
        yesterday = now - timedelta(days=1)
        start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    elif period == 'week':
        start = now - timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    
    elif period == 'month':
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    
    elif period == 'year':
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    
    else:
        start = now
        end = now
    
    return start, end


def sanitize_filename(filename):
    """Nettoyer un nom de fichier"""
    import re
    # Remplacer les caractères non alphanumériques par des underscores
    filename = re.sub(r'[^\w\s\-.]', '_', filename)
    # Remplacer les espaces multiples par un seul underscore
    filename = re.sub(r'\s+', '_', filename)
    return filename.lower()


def get_client_ip(request):
    """Récupérer l'IP du client depuis une requête"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def truncate_text(text, max_length=100, suffix='...'):
    """Tronquer un texte"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def parse_bool(value):
    """Parser une valeur booléenne depuis string"""
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        return value.lower() in ['true', '1', 'yes', 'oui', 'y']
    
    return bool(value)


def chunk_list(lst, chunk_size):
    """Diviser une liste en chunks"""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


def dict_to_query_string(params):
    """Convertir un dict en query string"""
    from urllib.parse import urlencode
    return urlencode(params)


def mask_sensitive_data(data, fields=['password', 'token', 'secret']):
    """Masquer les données sensibles dans un dict"""
    if not isinstance(data, dict):
        return data
    
    masked_data = data.copy()
    for key in masked_data:
        if any(field in key.lower() for field in fields):
            masked_data[key] = '***MASKED***'
        elif isinstance(masked_data[key], dict):
            masked_data[key] = mask_sensitive_data(masked_data[key], fields)
    
    return masked_data
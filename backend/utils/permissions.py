"""
Permissions et mixins utilitaires supplémentaires
"""
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


class RoleBasedPermission(permissions.BasePermission):
    """
    Permission basée sur les rôles avec configuration flexible
    
    Usage dans la view:
        permission_classes = [RoleBasedPermission]
        required_roles = ['admin', 'compagnie']
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Récupérer les rôles requis depuis la view
        required_roles = getattr(view, 'required_roles', None)
        
        if required_roles is None:
            # Si aucun rôle requis, autoriser
            return True
        
        # Vérifier si l'utilisateur a l'un des rôles requis
        return request.user.role in required_roles


class MethodBasedPermission(permissions.BasePermission):
    """
    Permission basée sur la méthode HTTP et le rôle
    
    Usage dans la view:
        permission_classes = [MethodBasedPermission]
        permission_map = {
            'GET': ['voyageur', 'compagnie', 'embarqueur', 'admin'],
            'POST': ['compagnie', 'admin'],
            'PUT': ['compagnie', 'admin'],
            'PATCH': ['compagnie', 'admin'],
            'DELETE': ['admin'],
        }
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Récupérer la map de permissions depuis la view
        permission_map = getattr(view, 'permission_map', {})
        
        if not permission_map:
            return True
        
        # Récupérer les rôles autorisés pour cette méthode
        allowed_roles = permission_map.get(request.method, [])
        
        if not allowed_roles:
            return False
        
        return request.user.role in allowed_roles


class ObjectOwnershipPermission(permissions.BasePermission):
    """
    Permission basée sur la propriété de l'objet
    
    Vérifie si l'utilisateur est propriétaire de l'objet via différents attributs
    """
    
    ownership_fields = ['user', 'passenger', 'owner', 'created_by']
    
    def has_object_permission(self, request, view, obj):
        # Admin a tous les droits
        if request.user.role == 'admin':
            return True
        
        # Vérifier la propriété via différents champs
        for field in self.ownership_fields:
            if hasattr(obj, field):
                owner = getattr(obj, field)
                if owner == request.user:
                    return True
        
        # Vérifier la propriété via la compagnie
        if hasattr(obj, 'company') and request.user.company:
            return obj.company == request.user.company
        
        return False


class CompanyOwnershipPermission(permissions.BasePermission):
    """
    Permission basée sur la propriété par la compagnie
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin a tous les droits
        if request.user.role == 'admin':
            return True
        
        # Vérifier que l'utilisateur appartient à une compagnie
        if not request.user.company:
            return False
        
        # Vérifier la propriété via la compagnie
        if hasattr(obj, 'company'):
            return obj.company == request.user.company
        
        return False


class ConditionalPermission(permissions.BasePermission):
    """
    Permission conditionnelle basée sur l'état de l'objet
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin peut toujours accéder
        if request.user.role == 'admin':
            return True
        
        # Récupérer les conditions depuis la view
        conditions = getattr(view, 'permission_conditions', {})
        
        for condition_field, allowed_values in conditions.items():
            if hasattr(obj, condition_field):
                if getattr(obj, condition_field) not in allowed_values:
                    return False
        
        return True


def check_permission(user, permission_name):
    """
    Fonction utilitaire pour vérifier une permission
    """
    permission_checks = {
        'can_create_trip': lambda u: u.role == 'compagnie' and u.company and u.company.is_approved,
        'can_validate_company': lambda u: u.role == 'admin',
        'can_scan_ticket': lambda u: u.role == 'embarqueur' and u.company,
        'can_manage_settings': lambda u: u.role == 'admin',
        'can_view_all_data': lambda u: u.role == 'admin',
        'can_export_data': lambda u: u.role in ['compagnie', 'admin'],
        'can_refund': lambda u: u.role == 'admin',
        'can_manage_claims': lambda u: u.role == 'admin',
    }
    
    check_func = permission_checks.get(permission_name)
    if check_func:
        return check_func(user)
    
    return False


def require_role(*roles):
    """
    Décorateur pour vérifier le rôle dans une fonction de view
    
    Usage:
        @require_role('admin', 'compagnie')
        def my_view(request):
            ...
    """
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied("Authentification requise.")
            
            if request.user.role not in roles:
                raise PermissionDenied(
                    f"Rôle requis: {', '.join(roles)}. Votre rôle: {request.user.role}"
                )
            
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_verified_account(func):
    """
    Décorateur pour exiger un compte vérifié
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied("Authentification requise.")
        
        if not request.user.is_verified:
            raise PermissionDenied("Vous devez vérifier votre compte.")
        
        return func(request, *args, **kwargs)
    return wrapper


def require_approved_company(func):
    """
    Décorateur pour exiger une compagnie approuvée
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied("Authentification requise.")
        
        if request.user.role != 'compagnie':
            raise PermissionDenied("Action réservée aux compagnies.")
        
        if not request.user.company or not request.user.company.is_approved:
            raise PermissionDenied("Votre compagnie doit être approuvée.")
        
        return func(request, *args, **kwargs)
    return wrapper


class DynamicPermission(permissions.BasePermission):
    """
    Permission dynamique qui peut être configurée au niveau de la view
    avec des règles personnalisées
    """
    
    def has_permission(self, request, view):
        # Récupérer la fonction de vérification depuis la view
        check_func = getattr(view, 'check_permission', None)
        
        if check_func and callable(check_func):
            return check_func(request)
        
        # Par défaut, autoriser
        return True
    
    def has_object_permission(self, request, view, obj):
        # Récupérer la fonction de vérification d'objet depuis la view
        check_func = getattr(view, 'check_object_permission', None)
        
        if check_func and callable(check_func):
            return check_func(request, obj)
        
        # Par défaut, autoriser
        return True


class IPWhitelistPermission(permissions.BasePermission):
    """
    Permission basée sur une whitelist d'IPs (pour webhooks, etc.)
    """
    
    def has_permission(self, request, view):
        # Récupérer la whitelist depuis les settings ou la view
        whitelist = getattr(view, 'ip_whitelist', [])
        
        if not whitelist:
            return True
        
        # Récupérer l'IP du client
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        return ip in whitelist


class MaintenanceModePermission(permissions.BasePermission):
    """
    Permission qui bloque l'accès si le mode maintenance est activé
    (sauf pour les admins)
    """
    
    message = "La plateforme est actuellement en maintenance. Veuillez réessayer plus tard."
    
    def has_permission(self, request, view):
        from apps.core.models import PlatformSettings
        
        settings = PlatformSettings.load()
        
        # Si pas en mode maintenance, autoriser
        if not settings.maintenance_mode:
            return True
        
        # Les admins peuvent accéder même en mode maintenance
        if request.user.is_authenticated and request.user.role == 'admin':
            return True
        
        return False
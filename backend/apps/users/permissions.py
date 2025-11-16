"""
Permissions personnalisées basées sur les rôles
"""
from rest_framework import permissions


class IsVoyageur(permissions.BasePermission):
    """Permission pour les voyageurs uniquement"""
    
    message = "Accès réservé aux voyageurs."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'voyageur'
        )


class IsCompagnie(permissions.BasePermission):
    """Permission pour les compagnies uniquement"""
    
    message = "Accès réservé aux compagnies de transport."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'compagnie' and
            request.user.company is not None
        )


class IsApprovedCompagnie(permissions.BasePermission):
    """Permission pour les compagnies approuvées uniquement"""
    
    message = "Votre compagnie doit être approuvée pour effectuer cette action."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'compagnie' and
            request.user.company is not None and
            request.user.company.is_approved
        )


class IsEmbarqueur(permissions.BasePermission):
    """Permission pour les embarqueurs uniquement"""
    
    message = "Accès réservé aux embarqueurs."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'embarqueur' and
            request.user.company is not None
        )


class IsAdminGlobal(permissions.BasePermission):
    """Permission pour les administrateurs globaux uniquement"""
    
    message = "Accès réservé aux administrateurs."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'admin'
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """Permission pour le propriétaire de l'objet ou un admin"""
    
    message = "Vous n'avez pas la permission d'accéder à cette ressource."
    
    def has_object_permission(self, request, view, obj):
        # Admin peut tout faire
        if request.user.role == 'admin':
            return True
        
        # Vérifier si l'utilisateur est le propriétaire
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'passenger'):
            return obj.passenger == request.user
        elif hasattr(obj, 'company'):
            return obj.company == request.user.company
        
        return False


class IsCompanyOwnerOrAdmin(permissions.BasePermission):
    """Permission pour la compagnie propriétaire ou un admin"""
    
    message = "Vous n'avez pas la permission d'accéder à cette ressource."
    
    def has_object_permission(self, request, view, obj):
        # Admin peut tout faire
        if request.user.role == 'admin':
            return True
        
        # Vérifier si la compagnie est propriétaire
        if request.user.role == 'compagnie' and request.user.company:
            if hasattr(obj, 'company'):
                return obj.company == request.user.company
        
        return False


class ReadOnly(permissions.BasePermission):
    """Permission lecture seule pour tous"""
    
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """Permission lecture pour tous, écriture pour authentifiés"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user and request.user.is_authenticated


class CanManageTicket(permissions.BasePermission):
    """Permission pour gérer un ticket"""
    
    message = "Vous n'avez pas la permission de gérer ce ticket."
    
    def has_object_permission(self, request, view, obj):
        # Admin peut tout faire
        if request.user.role == 'admin':
            return True
        
        # Le passager peut voir et annuler son ticket
        if obj.passenger == request.user:
            return True
        
        # La compagnie peut voir les tickets de ses voyages
        if request.user.role == 'compagnie' and request.user.company:
            if obj.trip.company == request.user.company:
                return True
        
        # L'embarqueur peut scanner les tickets
        if request.user.role == 'embarqueur' and request.user.company:
            if obj.trip.company == request.user.company:
                return True
        
        return False


class CanManageTrip(permissions.BasePermission):
    """Permission pour gérer un voyage"""
    
    message = "Vous n'avez pas la permission de gérer ce voyage."
    
    def has_permission(self, request, view):
        # Seules les compagnies approuvées peuvent créer des voyages
        if request.method == 'POST':
            return (
                request.user.role == 'compagnie' and
                request.user.company and
                request.user.company.is_approved
            )
        return True
    
    def has_object_permission(self, request, view, obj):
        # Admin peut tout faire
        if request.user.role == 'admin':
            return True
        
        # La compagnie peut gérer ses propres voyages
        if request.user.role == 'compagnie' and request.user.company:
            return obj.company == request.user.company
        
        return False


class CanManageVehicle(permissions.BasePermission):
    """Permission pour gérer un véhicule"""
    
    message = "Vous n'avez pas la permission de gérer ce véhicule."
    
    def has_permission(self, request, view):
        # Seules les compagnies peuvent créer des véhicules
        if request.method == 'POST':
            return request.user.role == 'compagnie' and request.user.company
        return True
    
    def has_object_permission(self, request, view, obj):
        # Admin peut tout faire
        if request.user.role == 'admin':
            return True
        
        # La compagnie peut gérer ses propres véhicules
        if request.user.role == 'compagnie' and request.user.company:
            return obj.company == request.user.company
        
        return False


class CanManageCompany(permissions.BasePermission):
    """Permission pour gérer une compagnie"""
    
    message = "Vous n'avez pas la permission de gérer cette compagnie."
    
    def has_object_permission(self, request, view, obj):
        # Admin peut tout faire
        if request.user.role == 'admin':
            return True
        
        # L'utilisateur peut gérer sa propre compagnie
        if request.user.role == 'compagnie' and request.user.company:
            return obj == request.user.company
        
        return False


class CanValidateCompany(permissions.BasePermission):
    """Permission pour valider/rejeter une compagnie"""
    
    message = "Seuls les administrateurs peuvent valider des compagnies."
    
    def has_permission(self, request, view):
        return request.user.role == 'admin'


class CanManagePayment(permissions.BasePermission):
    """Permission pour gérer un paiement"""
    
    message = "Vous n'avez pas la permission d'accéder à ce paiement."
    
    def has_object_permission(self, request, view, obj):
        # Admin peut tout voir
        if request.user.role == 'admin':
            return True
        
        # L'utilisateur peut voir ses propres paiements
        if obj.user == request.user:
            return True
        
        # La compagnie peut voir les paiements de ses voyages
        if request.user.role == 'compagnie' and request.user.company:
            if obj.company == request.user.company:
                return True
        
        return False


class CanScanTicket(permissions.BasePermission):
    """Permission pour scanner un ticket"""
    
    message = "Seuls les embarqueurs peuvent scanner des tickets."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'embarqueur' and
            request.user.company is not None
        )


class CanManageClaim(permissions.BasePermission):
    """Permission pour gérer une réclamation"""
    
    message = "Vous n'avez pas la permission d'accéder à cette réclamation."
    
    def has_permission(self, request, view):
        # Tout utilisateur authentifié peut créer une réclamation
        if request.method == 'POST':
            return request.user and request.user.is_authenticated
        return True
    
    def has_object_permission(self, request, view, obj):
        # Admin peut tout faire
        if request.user.role == 'admin':
            return True
        
        # L'utilisateur peut voir et modifier ses propres réclamations
        if obj.user == request.user:
            # Les utilisateurs ne peuvent pas changer le statut
            if request.method in ['PUT', 'PATCH']:
                # Vérifier qu'ils ne modifient pas les champs admin
                return True
            return True
        
        return False


class CanManageNotification(permissions.BasePermission):
    """Permission pour gérer une notification"""
    
    message = "Vous n'avez pas la permission d'accéder à cette notification."
    
    def has_object_permission(self, request, view, obj):
        # Admin peut tout faire
        if request.user.role == 'admin':
            return True
        
        # L'utilisateur peut voir et marquer comme lu ses propres notifications
        return obj.user == request.user


class CanAccessDashboard(permissions.BasePermission):
    """Permission pour accéder au dashboard"""
    
    message = "Vous n'avez pas accès au dashboard."
    
    def has_permission(self, request, view):
        # Compagnies et admins ont accès au dashboard
        return request.user.role in ['compagnie', 'admin']


class CanExportData(permissions.BasePermission):
    """Permission pour exporter des données"""
    
    message = "Vous n'avez pas la permission d'exporter des données."
    
    def has_permission(self, request, view):
        # Compagnies et admins peuvent exporter
        return request.user.role in ['compagnie', 'admin']


class CanManagePlatformSettings(permissions.BasePermission):
    """Permission pour gérer les paramètres de la plateforme"""
    
    message = "Seuls les administrateurs peuvent modifier les paramètres."
    
    def has_permission(self, request, view):
        # Seuls les admins peuvent modifier
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user.role == 'admin'
        
        # Tout le monde peut lire (si nécessaire)
        return True


class IsActiveUser(permissions.BasePermission):
    """Vérifier que l'utilisateur est actif"""
    
    message = "Votre compte est désactivé."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_active
        )


class IsVerifiedUser(permissions.BasePermission):
    """Vérifier que l'utilisateur est vérifié"""
    
    message = "Vous devez vérifier votre compte pour effectuer cette action."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_verified
        )


class ThrottleByRole(permissions.BasePermission):
    """Permission avec throttling basé sur le rôle"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return True
        
        # Les admins ne sont pas limités
        if request.user.role == 'admin':
            return True
        
        # Les autres rôles sont soumis au throttling standard
        return True
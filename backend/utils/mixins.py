"""
Mixins pour les ViewSets avec gestion des permissions
"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied


class RoleBasedViewSetMixin:
    """
    Mixin pour gérer les permissions basées sur les rôles dans les ViewSets
    """
    
    # Map action -> rôles autorisés
    role_permissions = {}
    
    def check_permissions(self, request):
        """Override pour ajouter la vérification des rôles"""
        super().check_permissions(request)
        
        # Vérifier les permissions spécifiques à l'action
        if self.role_permissions:
            action = self.action
            allowed_roles = self.role_permissions.get(action, [])
            
            if allowed_roles and request.user.role not in allowed_roles:
                raise PermissionDenied(
                    f"Votre rôle ({request.user.get_role_display()}) "
                    f"n'est pas autorisé pour cette action."
                )


class CompanyFilterMixin:
    """
    Mixin pour filtrer automatiquement les objets par compagnie
    """
    
    def get_queryset(self):
        """Filtrer par compagnie si l'utilisateur est une compagnie"""
        queryset = super().get_queryset()
        
        if self.request.user.role == 'compagnie' and self.request.user.company:
            # Filtrer par compagnie
            if hasattr(queryset.model, 'company'):
                queryset = queryset.filter(company=self.request.user.company)
        
        return queryset


class UserFilterMixin:
    """
    Mixin pour filtrer automatiquement les objets par utilisateur
    """
    
    def get_queryset(self):
        """Filtrer par utilisateur sauf pour les admins"""
        queryset = super().get_queryset()
        
        # Les admins voient tout
        if self.request.user.role == 'admin':
            return queryset
        
        # Filtrer par utilisateur
        user_field = getattr(self, 'user_field', 'user')
        
        if hasattr(queryset.model, user_field):
            filter_kwargs = {user_field: self.request.user}
            queryset = queryset.filter(**filter_kwargs)
        
        return queryset


class AuditMixin:
    """
    Mixin pour ajouter automatiquement created_by et updated_by
    """
    
    def perform_create(self, serializer):
        """Ajouter created_by lors de la création"""
        if hasattr(serializer.Meta.model, 'created_by'):
            serializer.save(created_by=self.request.user)
        else:
            serializer.save()
    
    def perform_update(self, serializer):
        """Ajouter updated_by lors de la mise à jour"""
        if hasattr(serializer.Meta.model, 'updated_by'):
            serializer.save(updated_by=self.request.user)
        else:
            serializer.save()
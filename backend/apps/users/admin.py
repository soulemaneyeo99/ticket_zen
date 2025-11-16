"""
Configuration Django Admin pour Users
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from apps.users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin personnalisé pour User"""
    
    list_display = ['email', 'get_full_name', 'role', 'company', 'is_active', 'is_verified', 'created_at']
    list_filter = ['role', 'is_active', 'is_verified', 'created_at']
    search_fields = ['email', 'first_name', 'last_name', 'phone_number']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Informations personnelles'), {
            'fields': ('first_name', 'last_name', 'phone_number', 'avatar')
        }),
        (_('Rôle et Compagnie'), {
            'fields': ('role', 'company')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Dates importantes'), {
            'fields': ('last_login', 'last_login_ip', 'created_at', 'updated_at')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone_number', 'role', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login', 'last_login_ip']
    
    def get_queryset(self, request):
        """Optimiser les requêtes"""
        return super().get_queryset(request).select_related('company')
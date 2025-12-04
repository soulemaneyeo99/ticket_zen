"""
Configuration Django Admin pour Logs
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from apps.logs.models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    """Admin pour ActivityLog (lecture seule)"""
    
    list_display = [
        'created_at', 'user_info', 'action_display',
        'severity_badge', 'ip_address', 'description_short'
    ]
    list_filter = ['action', 'severity', 'created_at']
    search_fields = ['description', 'user__email', 'ip_address']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user', 'ip_address', 'user_agent')
        }),
        ('Action', {
            'fields': ('action', 'description', 'severity')
        }),
        ('Détails', {
            'fields': ('details', 'tags')
        }),
        ('Objet concerné', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        }),
        ('Date', {
            'fields': ('created_at',)
        }),
    )
    
    readonly_fields = [
        'user', 'action', 'description', 'details', 'ip_address',
        'user_agent', 'content_type', 'object_id', 'severity',
        'tags', 'created_at'
    ]
    
    def has_add_permission(self, request):
        """Désactiver l'ajout depuis l'admin"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Désactiver la suppression depuis l'admin"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Désactiver la modification depuis l'admin"""
        return False
    
    def user_info(self, obj):
        """Afficher les infos utilisateur"""
        if obj.user:
            return format_html(
                '<strong>{}</strong><br/><small>{}</small>',
                obj.user.get_full_name(),
                obj.user.email
            )
        return 'Système'
    user_info.short_description = 'Utilisateur'
    
    def action_display(self, obj):
        """Afficher l'action"""
        return obj.get_action_display()
    action_display.short_description = 'Action'
    
    def severity_badge(self, obj):
        """Badge de sévérité"""
        colors = {
            'info': 'blue',
            'warning': 'orange',
            'error': 'red',
            'critical': 'darkred'
        }
        color = colors.get(obj.severity, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_severity_display()
        )
    severity_badge.short_description = 'Sévérité'
    
    def description_short(self, obj):
        """Description tronquée"""
        return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description
    description_short.short_description = 'Description'
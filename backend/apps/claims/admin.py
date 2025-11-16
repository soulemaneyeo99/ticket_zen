"""
Configuration Django Admin pour Claims
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from apps.claims.models import Claim, ClaimMessage


class ClaimMessageInline(admin.TabularInline):
    """Inline pour les messages de réclamation"""
    model = ClaimMessage
    extra = 0
    readonly_fields = ['sender', 'message', 'is_internal', 'created_at']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    """Admin pour Claim"""
    
    list_display = [
        'id', 'subject_short', 'user_info', 'category',
        'priority_badge', 'status_badge', 'assigned_to',
        'created_at', 'resolved_at'
    ]
    list_filter = ['status', 'priority', 'category', 'created_at']
    search_fields = ['subject', 'description', 'user__email']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Réclamation', {
            'fields': ('category', 'subject', 'description')
        }),
        ('Références', {
            'fields': ('ticket', 'trip'),
            'classes': ('collapse',)
        }),
        ('Pièces jointes', {
            'fields': ('attachment_1', 'attachment_2', 'attachment_3'),
            'classes': ('collapse',)
        }),
        ('Gestion', {
            'fields': ('status', 'priority', 'assigned_to')
        }),
        ('Réponse', {
            'fields': ('admin_response', 'resolution_notes')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at', 'resolved_at', 'closed_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'resolved_at', 'closed_at']
    
    inlines = [ClaimMessageInline]
    
    def subject_short(self, obj):
        """Sujet tronqué"""
        return obj.subject[:50] + '...' if len(obj.subject) > 50 else obj.subject
    subject_short.short_description = 'Sujet'
    
    def user_info(self, obj):
        """Infos utilisateur"""
        return format_html(
            '<strong>{}</strong><br/><small>{}</small>',
            obj.user.get_full_name(),
            obj.user.email
        )
    user_info.short_description = 'Utilisateur'
    
    def priority_badge(self, obj):
        """Badge de priorité"""
        colors = {
            'low': 'green',
            'medium': 'orange',
            'high': 'red',
            'urgent': 'darkred'
        }
        color = colors.get(obj.priority, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Priorité'
    
    def status_badge(self, obj):
        """Badge de statut"""
        colors = {
            'open': 'orange',
            'in_progress': 'blue',
            'resolved': 'green',
            'closed': 'gray',
            'rejected': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Statut'
    
    actions = ['resolve_claims', 'close_claims', 'set_high_priority']
    
    def resolve_claims(self, request, queryset):
        """Résoudre les réclamations"""
        from django.utils import timezone
        
        updated = queryset.filter(status__in=[Claim.OPEN, Claim.IN_PROGRESS]).update(
            status=Claim.RESOLVED,
            resolved_at=timezone.now()
        )
        self.message_user(request, f'{updated} réclamation(s) résolue(s)')
    resolve_claims.short_description = 'Marquer comme résolues'
    
    def close_claims(self, request, queryset):
        """Fermer les réclamations"""
        from django.utils import timezone
        
        updated = queryset.update(status=Claim.CLOSED, closed_at=timezone.now())
        self.message_user(request, f'{updated} réclamation(s) fermée(s)')
    close_claims.short_description = 'Fermer les réclamations'
    
    def set_high_priority(self, request, queryset):
        """Définir priorité haute"""
        updated = queryset.update(priority=Claim.HIGH)
        self.message_user(request, f'{updated} réclamation(s) en priorité haute')
    set_high_priority.short_description = 'Priorité haute'
@admin.register(ClaimMessage)
class ClaimMessageAdmin(admin.ModelAdmin):
    list_display = ['claim', 'sender', 'message_short', 'is_internal', 'created_at']
    list_filter = ['is_internal', 'created_at']
    search_fields = ['message', 'sender__email']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    readonly_fields = ['claim', 'sender', 'message', 'is_internal', 'attachment', 'created_at']

    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False

    def message_short(self, obj):
        """Message tronqué"""
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    message_short.short_description = 'Message'
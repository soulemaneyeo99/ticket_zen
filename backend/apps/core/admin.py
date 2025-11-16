## 📁 apps/core/admin.py (CORRIGÉ)
"""
Configuration Django Admin pour Core
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from apps.core.models import PlatformSettings, FAQ, Banner


@admin.register(PlatformSettings)
class PlatformSettingsAdmin(admin.ModelAdmin):
    """Admin pour PlatformSettings (singleton)"""
    
    fieldsets = (
        ('Commissions', {
            'fields': ('default_commission_rate',)
        }),
        ('Délais et limites', {
            'fields': (
                'ticket_cancellation_deadline_hours',
                'payment_timeout_minutes',
                'qr_code_expiration_hours',
                'max_tickets_per_booking'
            )
        }),
        ('Prix', {
            'fields': ('min_ticket_price', 'max_ticket_price')
        }),
        ('Notifications', {
            'fields': (
                'send_email_notifications',
                'send_sms_notifications',
                'trip_reminder_hours_before'
            )
        }),
        ('Réservations', {
            'fields': (
                'allow_overbooking',
                'overbooking_percentage'
            )
        }),
        ('Maintenance', {
            'fields': ('maintenance_mode', 'maintenance_message')
        }),
        ('Contact', {
            'fields': ('support_email', 'support_phone')
        }),
        ('Informations', {
            'fields': ('updated_at', 'updated_by')
        }),
    )
    
    readonly_fields = ['updated_at', 'updated_by']
    
    def has_add_permission(self, request):
        """Désactiver l'ajout (singleton)"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Désactiver la suppression (singleton)"""
        return False


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    """Admin pour FAQ"""
    
    list_display = ['question_short', 'category', 'order', 'is_active', 'views', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['question', 'answer']
    ordering = ['category', 'order', '-views']
    
    fieldsets = (
        ('Catégorie', {
            'fields': ('category',)
        }),
        ('Contenu', {
            'fields': ('question', 'answer')
        }),
        ('Paramètres', {
            'fields': ('order', 'is_active')
        }),
        ('Statistiques', {
            'fields': ('views',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['views', 'created_at', 'updated_at']
    
    def question_short(self, obj):
        """Question tronquée"""
        return obj.question[:80] + '...' if len(obj.question) > 80 else obj.question
    question_short.short_description = 'Question'


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    """Admin pour Banner"""
    
    list_display = [
        'title', 'is_visible_badge', 'start_date', 'end_date',
        'views', 'clicks', 'ctr_display', 'order'
    ]
    list_filter = ['is_active', 'start_date', 'end_date', 'target_role']
    search_fields = ['title', 'description']
    ordering = ['order', '-created_at']
    
    fieldsets = (
        ('Contenu', {
            'fields': ('title', 'description', 'image', 'link_url')
        }),
        ('Affichage', {
            'fields': ('is_active', 'start_date', 'end_date', 'order')
        }),
        ('Ciblage', {
            'fields': ('target_role',)
        }),
        ('Statistiques', {
            'fields': ('views', 'clicks'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['views', 'clicks', 'created_at', 'updated_at']
    
    def is_visible_badge(self, obj):
        """Badge de visibilité"""
        if obj.is_visible:
            return format_html(
                '<span style="background-color: green; color: white; padding: 3px 10px; border-radius: 3px;">Visible</span>'
            )
        return format_html(
            '<span style="background-color: gray; color: white; padding: 3px 10px; border-radius: 3px;">Masquée</span>'
        )
    is_visible_badge.short_description = 'Visibilité'
    
    def ctr_display(self, obj):
        """Afficher le CTR"""
        return f'{obj.click_through_rate:.2f}%'
    ctr_display.short_description = 'CTR'

"""
Configuration Django Admin pour Payments
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from apps.payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin pour Payment"""
    
    list_display = [
        'transaction_id', 'user_info', 'amount', 'payment_method',
        'status_badge', 'created_at', 'completed_at'
    ]
    list_filter = ['status', 'payment_method', 'company', 'created_at']
    search_fields = ['transaction_id', 'provider_transaction_id', 'user__email', 'phone_number']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Transaction', {
            'fields': ('transaction_id', 'provider_transaction_id')
        }),
        ('Utilisateur et voyage', {
            'fields': ('user', 'trip', 'company')
        }),
        ('Montants', {
            'fields': ('amount', 'platform_commission', 'company_amount')
        }),
        ('Méthode de paiement', {
            'fields': ('payment_method', 'phone_number')
        }),
        ('Statut', {
            'fields': ('status', 'payment_url')
        }),
        ('Réponse provider', {
            'fields': ('provider_response',),
            'classes': ('collapse',)
        }),
        ('Remboursement', {
            'fields': ('refund_transaction_id', 'refund_amount', 'refund_reason', 'refunded_at'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = [
        'transaction_id', 'provider_transaction_id', 'platform_commission',
        'company_amount', 'provider_response', 'created_at', 'updated_at',
        'completed_at', 'refunded_at'
    ]
    
    def user_info(self, obj):
        """Afficher les infos utilisateur"""
        return format_html(
            '<strong>{}</strong><br/><small>{}</small>',
            obj.user.get_full_name(),
            obj.user.email
        )
    user_info.short_description = 'Utilisateur'
    
    def status_badge(self, obj):
        """Badge du statut"""
        colors = {
            'pending': 'orange',
            'processing': 'blue',
            'success': 'green',
            'failed': 'red',
            'cancelled': 'gray',
            'refunded': 'purple'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Statut'
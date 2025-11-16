"""
Configuration Django Admin pour Notifications
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from apps.notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin pour Notification"""
    
    list_display = [
        'title_short', 'user_info', 'notification_type',
        'category', 'status_badge', 'created_at', 'sent_at'
    ]
    list_filter = ['notification_type', 'category', 'status', 'created_at']
    search_fields = ['title', 'message', 'user__email']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Destinataire', {
            'fields': ('user', 'recipient_email', 'recipient_phone')
        }),
        ('Type et catégorie', {
            'fields': ('notification_type', 'category')
        }),
        ('Contenu', {
            'fields': ('title', 'message', 'html_content', 'action_url')
        }),
        ('Métadonnées', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Statut et envoi', {
            'fields': ('status', 'sent_at', 'read_at')
        }),
        ('Tentatives', {
            'fields': ('attempts', 'max_attempts', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Planification', {
            'fields': ('scheduled_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['sent_at', 'read_at', 'created_at', 'updated_at']
    
    def title_short(self, obj):
        """Titre tronqué"""
        return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
    title_short.short_description = 'Titre'
    
    def user_info(self, obj):
        """Infos utilisateur"""
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
            'sent': 'green',
            'failed': 'red',
            'read': 'blue'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Statut'
    
    actions = ['resend_notifications', 'mark_as_read']
    
    def resend_notifications(self, request, queryset):
        """Renvoyer les notifications"""
        for notification in queryset.filter(status__in=[Notification.FAILED, Notification.PENDING]):
            from apps.notifications.tasks import send_email_notification, send_sms_notification
            
            if notification.notification_type == Notification.EMAIL:
                send_email_notification.delay(notification.id)
            elif notification.notification_type == Notification.SMS:
                send_sms_notification.delay(notification.id)
        
        self.message_user(request, f'{queryset.count()} notification(s) renvoyée(s)')
    resend_notifications.short_description = 'Renvoyer les notifications'
    
    def mark_as_read(self, request, queryset):
        """Marquer comme lu"""
        from django.utils import timezone
        
        updated = queryset.update(status=Notification.READ, read_at=timezone.now())
        self.message_user(request, f'{updated} notification(s) marquée(s) comme lue(s)')
    mark_as_read.short_description = 'Marquer comme lues'
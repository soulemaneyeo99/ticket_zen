"""
Configuration Django Admin pour Tickets
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from apps.tickets.models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """Admin pour Ticket"""
    
    list_display = [
        'ticket_number', 'passenger_info', 'trip_info',
        'seat_number', 'total_amount', 'status_badge',
        'is_paid', 'created_at'
    ]
    list_filter = ['status', 'is_paid', 'trip__company', 'created_at']
    search_fields = [
        'ticket_number', 'passenger_first_name', 'passenger_last_name',
        'passenger_email', 'passenger_phone'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informations ticket', {
            'fields': ('ticket_number', 'trip', 'passenger')
        }),
        ('Informations passager', {
            'fields': (
                'passenger_first_name', 'passenger_last_name',
                'passenger_phone', 'passenger_email', 'passenger_id_number'
            )
        }),
        ('Siège', {
            'fields': ('seat_number',)
        }),
        ('Prix', {
            'fields': ('price', 'platform_fee', 'total_amount')
        }),
        ('Statut', {
            'fields': ('status', 'is_paid')
        }),
        ('Paiement', {
            'fields': ('payment',)
        }),
        ('QR Code', {
            'fields': ('qr_code', 'qr_code_image'),
            'classes': ('collapse',)
        }),
        ('Embarquement', {
            'fields': ('boarding_time', 'boarded_by'),
            'classes': ('collapse',)
        }),
        ('Annulation', {
            'fields': ('cancelled_at', 'cancellation_reason', 'refund_amount'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at', 'confirmed_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = [
        'ticket_number', 'total_amount', 'qr_code', 'qr_code_image',
        'boarding_time', 'boarded_by', 'cancelled_at',
        'created_at', 'updated_at', 'confirmed_at'
    ]
    
    def passenger_info(self, obj):
        """Afficher les infos du passager"""
        return format_html(
            '<strong>{}</strong><br/><small>{}</small>',
            obj.passenger_full_name,
            obj.passenger_email
        )
    passenger_info.short_description = 'Passager'
    
    def trip_info(self, obj):
        """Afficher les infos du voyage"""
        return format_html(
            '{} → {}<br/><small>{}</small>',
            obj.trip.departure_city.name,
            obj.trip.arrival_city.name,
            obj.trip.departure_datetime.strftime('%d/%m/%Y %H:%M')
        )
    trip_info.short_description = 'Voyage'
    
    def status_badge(self, obj):
        """Badge du statut"""
        colors = {
            'pending': 'orange',
            'confirmed': 'green',
            'cancelled': 'red',
            'used': 'blue',
            'expired': 'gray',
            'refunded': 'purple'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Statut'
    
    actions = ['cancel_tickets', 'confirm_tickets']
    
    def cancel_tickets(self, request, queryset):
        """Annuler les tickets sélectionnés"""
        from django.utils import timezone
        
        updated = 0
        for ticket in queryset:
            if ticket.can_be_cancelled:
                ticket.status = Ticket.CANCELLED
                ticket.cancelled_at = timezone.now()
                ticket.save()
                updated += 1
        
        self.message_user(request, f'{updated} ticket(s) annulé(s)')
    cancel_tickets.short_description = 'Annuler les tickets (si possible)'
    
    def confirm_tickets(self, request, queryset):
        """Confirmer les tickets"""
        from django.utils import timezone
        
        updated = queryset.filter(status=Ticket.PENDING).update(
            status=Ticket.CONFIRMED,
            confirmed_at=timezone.now()
        )
        self.message_user(request, f'{updated} ticket(s) confirmé(s)')
    confirm_tickets.short_description = 'Confirmer les tickets en attente'
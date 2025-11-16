"""
Configuration Django Admin pour Boarding
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from apps.boarding.models import BoardingPass


@admin.register(BoardingPass)
class BoardingPassAdmin(admin.ModelAdmin):
    """Admin pour BoardingPass"""
    
    list_display = [
        'ticket_number_display', 'trip_info', 'boarding_agent_name',
        'scan_status_badge', 'is_offline_scan', 'scanned_at'
    ]
    list_filter = ['scan_status', 'is_offline_scan', 'trip__company', 'scanned_at']
    search_fields = ['ticket__ticket_number', 'boarding_agent__email']
    date_hierarchy = 'scanned_at'
    ordering = ['-scanned_at']
    
    fieldsets = (
        ('Ticket et voyage', {
            'fields': ('ticket', 'trip')
        }),
        ('Embarqueur', {
            'fields': ('boarding_agent',)
        }),
        ('Scan', {
            'fields': ('scan_status', 'scanned_at')
        }),
        ('Localisation', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Mode offline', {
            'fields': ('is_offline_scan', 'synced_at', 'device_info'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['scanned_at', 'synced_at']
    
    def ticket_number_display(self, obj):
        """Afficher le numéro de ticket"""
        return obj.ticket.ticket_number
    ticket_number_display.short_description = 'N° Ticket'
    
    def trip_info(self, obj):
        """Afficher les infos du voyage"""
        return format_html(
            '{} → {}',
            obj.trip.departure_city.name,
            obj.trip.arrival_city.name
        )
    trip_info.short_description = 'Voyage'
    
    def boarding_agent_name(self, obj):
        """Nom de l'embarqueur"""
        return obj.boarding_agent.get_full_name() if obj.boarding_agent else 'N/A'
    boarding_agent_name.short_description = 'Embarqueur'
    
    def scan_status_badge(self, obj):
        """Badge du statut de scan"""
        colors = {
            'valid': 'green',
            'invalid': 'red',
            'already_used': 'orange',
            'expired': 'gray',
            'wrong_trip': 'purple'
        }
        color = colors.get(obj.scan_status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_scan_status_display()
        )
    scan_status_badge.short_description = 'Statut scan'
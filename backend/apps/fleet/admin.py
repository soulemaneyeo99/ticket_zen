"""
Configuration Django Admin pour Fleet
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from apps.fleet.models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    """Admin pour Vehicle"""
    
    list_display = [
        'registration_number', 'company', 'vehicle_type', 'brand', 'model',
        'total_seats', 'status_badge', 'is_active', 'created_at'
    ]
    list_filter = ['vehicle_type', 'status', 'is_active', 'company', 'brand']
    search_fields = ['registration_number', 'brand', 'model', 'company__name']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Compagnie', {
            'fields': ('company',)
        }),
        ('Informations du véhicule', {
            'fields': ('vehicle_type', 'registration_number', 'brand', 'model', 'year', 'color')
        }),
        ('Capacité', {
            'fields': ('total_seats', 'seat_configuration')
        }),
        ('Équipements', {
            'fields': ('has_ac', 'has_wifi', 'has_tv', 'has_usb_ports', 'has_toilet')
        }),
        ('Photos', {
            'fields': ('photo_main', 'photo_interior')
        }),
        ('Statut', {
            'fields': ('status', 'is_active')
        }),
        ('Documents et maintenance', {
            'fields': (
                'insurance_expiry', 'technical_inspection_expiry',
                'last_maintenance_date', 'next_maintenance_date', 'maintenance_notes'
            ),
            'classes': ('collapse',)
        }),
        ('Statistiques', {
            'fields': ('total_trips', 'total_km'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['total_trips', 'total_km', 'created_at', 'updated_at']
    
    def status_badge(self, obj):
        """Badge coloré pour le statut"""
        colors = {
            'active': 'green',
            'maintenance': 'orange',
            'inactive': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Statut'
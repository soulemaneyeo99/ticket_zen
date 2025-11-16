"""
Configuration Django Admin pour Trips
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from apps.trips.models import Trip, City


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    """Admin pour City"""
    
    list_display = ['name', 'country', 'is_active', 'created_at']
    list_filter = ['country', 'is_active']
    search_fields = ['name', 'country']
    ordering = ['name']
    
    fieldsets = (
        (_('Informations'), {
            'fields': ('name', 'slug', 'country')
        }),
        (_('Coordonnées'), {
            'fields': ('latitude', 'longitude')
        }),
        (_('Statut'), {
            'fields': ('is_active',)
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Slug readonly seulement en édition"""
        if obj:
            return ['slug', 'created_at', 'updated_at']
        return ['created_at', 'updated_at']
    
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    """Admin pour Trip"""
    
    list_display = [
        'trip_info', 'company', 'departure_datetime', 'base_price',
        'seats_info', 'occupancy_badge', 'status_badge', 'is_active'
    ]
    list_filter = ['status', 'is_active', 'company', 'departure_city', 'arrival_city', 'departure_datetime']
    search_fields = ['company__name', 'departure_city__name', 'arrival_city__name']
    date_hierarchy = 'departure_datetime'
    ordering = ['-departure_datetime']
    
    fieldsets = (
        (_('Compagnie et véhicule'), {
            'fields': ('company', 'vehicle')
        }),
        (_('Trajet'), {
            'fields': (
                'departure_city', 'arrival_city',
                'departure_location', 'arrival_location'
            )
        }),
        (_('Date et heure'), {
            'fields': (
                'departure_datetime', 'estimated_arrival_datetime',
                'actual_departure_datetime', 'actual_arrival_datetime',
                'estimated_duration', 'distance_km'
            )
        }),
        (_('Prix et places'), {
            'fields': ('base_price', 'total_seats', 'available_seats', 'reserved_seats')
        }),
        (_('Statut'), {
            'fields': ('status', 'is_active', 'is_recurring')
        }),
        (_('Annulation'), {
            'fields': ('allows_cancellation', 'cancellation_deadline_hours')
        }),
        (_('Embarqueurs'), {
            'fields': ('boarding_agents',)
        }),
        (_('Notes'), {
            'fields': ('notes', 'driver_notes'),
            'classes': ('collapse',)
        }),
        (_('Statistiques financières'), {
            'fields': ('total_revenue', 'commission_amount'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['total_seats', 'available_seats', 'reserved_seats', 'total_revenue', 'commission_amount']
    
    filter_horizontal = ['boarding_agents']
    
    def trip_info(self, obj):
        """Afficher les infos du trajet"""
        return format_html(
            '<strong>{}</strong> → <strong>{}</strong>',
            obj.departure_city.name,
            obj.arrival_city.name
        )
    trip_info.short_description = 'Trajet'
    
    def seats_info(self, obj):
        """Afficher les infos sur les sièges"""
        return f'{obj.available_seats}/{obj.total_seats}'
    seats_info.short_description = 'Places dispo/total'
    
    def occupancy_badge(self, obj):
        """Badge du taux d'occupation"""
        rate = obj.occupancy_rate
        if rate >= 90:
            color = 'red'
        elif rate >= 70:
            color = 'orange'
        else:
            color = 'green'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{:.1f}%</span>',
            color,
            rate
        )
    occupancy_badge.short_description = 'Taux occupation'
    
    def status_badge(self, obj):
        """Badge du statut"""
        colors = {
            'scheduled': 'blue',
            'boarding': 'orange',
            'in_progress': 'purple',
            'completed': 'green',
            'cancelled': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Statut'
    
    actions = ['cancel_trips', 'activate_trips', 'deactivate_trips']
    
    def cancel_trips(self, request, queryset):
        """Annuler les voyages sélectionnés"""
        updated = queryset.update(status=Trip.CANCELLED)
        self.message_user(request, f'{updated} voyage(s) annulé(s)')
    cancel_trips.short_description = 'Annuler les voyages sélectionnés'
    
    def activate_trips(self, request, queryset):
        """Activer les voyages"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} voyage(s) activé(s)')
    activate_trips.short_description = 'Activer les voyages'
    
    def deactivate_trips(self, request, queryset):
        """Désactiver les voyages"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} voyage(s) désactivé(s)')
    deactivate_trips.short_description = 'Désactiver les voyages'
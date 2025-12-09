"""
Configuration Django Admin pour Companies (avec prepopulated_fields)
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from apps.companies.models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """Admin pour Company"""
    
    list_display = [
        'name', 'city', 'status_badge', 'is_active', 
        'total_trips', 'total_tickets_sold', 'total_revenue', 
        'created_at'
    ]
    list_filter = ['status', 'is_active', 'city', 'created_at']
    search_fields = ['name', 'email', 'registration_number', 'phone_number']
    ordering = ['-created_at']
    
    fieldsets = (
        (_('Informations de base'), {
            'fields': ('name', 'slug', 'logo')  # Ajouter slug ici
        }),
        (_('Informations légales'), {
            'fields': ('registration_number', 'tax_id', 'license_document', 'insurance_document')
        }),
        (_('Contact'), {
            'fields': ('email', 'phone_number', 'address', 'city', 'country')
        }),
        (_('Présentation'), {
            'fields': ('description',)
        }),
        (_('Statut et validation'), {
            'fields': ('status', 'is_active', 'admin_notes', 'validated_by', 'validated_at')
        }),
        (_('Commission'), {
            'fields': ('commission_rate',)
        }),
        (_('Statistiques'), {
            'fields': ('total_trips', 'total_tickets_sold', 'total_revenue'),
            'classes': ('collapse',)
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Maintenant readonly_fields ne contient plus 'slug' lors de l'ajout
    def get_readonly_fields(self, request, obj=None):
        """Rendre slug readonly seulement lors de l'édition"""
        if obj:  # Si on édite un objet existant
            return [
                'slug', 'total_trips', 'total_tickets_sold', 'total_revenue',
                'validated_by', 'validated_at', 'created_at', 'updated_at'
            ]
        else:  # Si on crée un nouvel objet
            return [
                'total_trips', 'total_tickets_sold', 'total_revenue',
                'validated_by', 'validated_at', 'created_at', 'updated_at'
            ]
    
    prepopulated_fields = {'slug': ('name',)}
    
    actions = ['approve_companies', 'reject_companies', 'suspend_companies']
    
    def status_badge(self, obj):
        """Afficher le statut avec badge coloré"""
        colors = {
            'pending': 'orange',
            'approved': 'green',
            'rejected': 'red',
            'suspended': 'gray'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Statut'
    
    def approve_companies(self, request, queryset):
        """Action pour approuver des compagnies"""
        from django.utils import timezone
        
        updated = queryset.update(
            status=Company.APPROVED,
            validated_by=request.user,
            validated_at=timezone.now()
        )
        self.message_user(request, f'{updated} compagnie(s) approuvée(s)')
    approve_companies.short_description = 'Approuver les compagnies sélectionnées'
    
    def reject_companies(self, request, queryset):
        """Action pour rejeter des compagnies"""
        from django.utils import timezone
        
        updated = queryset.update(
            status=Company.REJECTED,
            validated_by=request.user,
            validated_at=timezone.now()
        )
        self.message_user(request, f'{updated} compagnie(s) rejetée(s)')
    reject_companies.short_description = 'Rejeter les compagnies sélectionnées'
    
    def suspend_companies(self, request, queryset):
        """Action pour suspendre des compagnies"""
        updated = queryset.update(status=Company.SUSPENDED, is_active=False)
        self.message_user(request, f'{updated} compagnie(s) suspendue(s)')
    suspend_companies.short_description = 'Suspendre les compagnies sélectionnées'
"""
Filtres personnalisés pour les APIs
"""
from django_filters import rest_framework as filters
from apps.trips.models import Trip
from apps.tickets.models import Ticket
from apps.payments.models import Payment


class TripFilter(filters.FilterSet):
    """Filtre avancé pour les voyages"""
    
    departure_city = filters.NumberFilter(field_name='departure_city__id')
    arrival_city = filters.NumberFilter(field_name='arrival_city__id')
    departure_date = filters.DateFilter(field_name='departure_datetime__date')
    departure_date_from = filters.DateFilter(field_name='departure_datetime__date', lookup_expr='gte')
    departure_date_to = filters.DateFilter(field_name='departure_datetime__date', lookup_expr='lte')
    min_price = filters.NumberFilter(field_name='base_price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='base_price', lookup_expr='lte')
    min_seats = filters.NumberFilter(field_name='available_seats', lookup_expr='gte')
    company = filters.NumberFilter(field_name='company__id')
    
    class Meta:
        model = Trip
        fields = [
            'departure_city', 'arrival_city', 'departure_date',
            'departure_date_from', 'departure_date_to',
            'min_price', 'max_price', 'min_seats', 'company', 'status'
        ]


class TicketFilter(filters.FilterSet):
    """Filtre avancé pour les tickets"""
    
    passenger = filters.NumberFilter(field_name='passenger__id')
    trip = filters.UUIDFilter(field_name='trip__id')
    status = filters.ChoiceFilter(choices=Ticket.STATUS_CHOICES)
    is_paid = filters.BooleanFilter()
    created_date_from = filters.DateFilter(field_name='created_at__date', lookup_expr='gte')
    created_date_to = filters.DateFilter(field_name='created_at__date', lookup_expr='lte')
    
    class Meta:
        model = Ticket
        fields = ['passenger', 'trip', 'status', 'is_paid', 'created_date_from', 'created_date_to']


class PaymentFilter(filters.FilterSet):
    """Filtre avancé pour les paiements"""
    
    user = filters.NumberFilter(field_name='user__id')
    company = filters.NumberFilter(field_name='company__id')
    status = filters.ChoiceFilter(choices=Payment.STATUS_CHOICES)
    payment_method = filters.ChoiceFilter(choices=Payment.PAYMENT_METHOD_CHOICES)
    amount_min = filters.NumberFilter(field_name='amount', lookup_expr='gte')
    amount_max = filters.NumberFilter(field_name='amount', lookup_expr='lte')
    created_date_from = filters.DateFilter(field_name='created_at__date', lookup_expr='gte')
    created_date_to = filters.DateFilter(field_name='created_at__date', lookup_expr='lte')
    
    class Meta:
        model = Payment
        fields = [
            'user', 'company', 'status', 'payment_method',
            'amount_min', 'amount_max', 'created_date_from', 'created_date_to'
        ]
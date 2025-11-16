"""
Classes de pagination personnalisées
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict


class StandardResultsSetPagination(PageNumberPagination):
    """Pagination standard avec métadonnées enrichies"""
    
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """Retourner une réponse avec métadonnées complètes"""
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.get_page_size(self.request)),
            ('results', data)
        ]))


class LargeResultsSetPagination(PageNumberPagination):
    """Pagination pour larges datasets"""
    
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500


class SmallResultsSetPagination(PageNumberPagination):
    """Pagination pour petits datasets"""
    
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
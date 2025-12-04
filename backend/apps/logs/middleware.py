"""
Middleware pour logger automatiquement les activités
"""
from django.utils import timezone
from apps.logs.models import ActivityLog
from django.utils.deprecation import MiddlewareMixin


class ActivityLogMiddleware(MiddlewareMixin):
    """Middleware pour logger automatiquement certaines requêtes"""
    
    # Actions à logger automatiquement
    LOG_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
    
    # URLs à ignorer
    IGNORE_URLS = [
        '/admin/',
        '/static/',
        '/media/',
        '/api/schema/',
        '/api/docs/',
    ]
    
    def process_request(self, request):
        """Traiter la requête entrante"""
        request._activity_log_start_time = timezone.now()
        return None
    
    def process_response(self, request, response):
        """Traiter la réponse sortante"""
        # Ignorer certaines URLs
        if any(request.path.startswith(url) for url in self.IGNORE_URLS):
            return response
        
        # Logger uniquement certaines méthodes
        if request.method not in self.LOG_METHODS:
            return response
        
        # Logger uniquement si l'utilisateur est authentifié
        if not request.user.is_authenticated:
            return response
        
        # Ne pas logger les succès routiers (GET, etc.)
        if response.status_code < 400:
            return response
        
        # Logger l'erreur
        try:
            ActivityLog.objects.create(
                user=request.user,
                action=ActivityLog.ADMIN_ACTION,
                description=f"{request.method} {request.path} - {response.status_code}",
                details={
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                },
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                severity=ActivityLog.SEVERITY_ERROR if response.status_code >= 500 else ActivityLog.SEVERITY_WARNING
            )
        except Exception:
            # Ne pas casser la requête si le logging échoue
            pass
        
        return response
    
    @staticmethod
    def _get_client_ip(request):
        """Récupérer l'IP du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
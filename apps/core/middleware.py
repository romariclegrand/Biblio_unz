from apps.statistics.models import LogActivite

class LogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        if request.user.is_authenticated:
            path = request.path
            if path == '/users/login/' and request.method == 'POST':
                LogActivite.objects.create(
                    utilisateur=request.user,
                    action='connexion',
                    details=f"Connexion depuis {request.META.get('REMOTE_ADDR', 'inconnue')}",
                    ip_address=request.META.get('REMOTE_ADDR')
                )
            elif path == '/users/logout/':
                LogActivite.objects.create(
                    utilisateur=request.user,
                    action='deconnexion',
                    details="Déconnexion",
                    ip_address=request.META.get('REMOTE_ADDR')
                )
        
        return response

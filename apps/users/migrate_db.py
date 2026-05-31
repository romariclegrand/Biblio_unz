from django.http import JsonResponse
from django.core.management import call_command
from django.views.decorators.csrf import csrf_exempt
from django.db import connections

@csrf_exempt
def run_migrations(request):
    try:
        connections['default'].cursor()
        call_command('migrate', interactive=False, verbosity=0)
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='Principal',
                role='administrateur'
            )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Migrations exécutées et superutilisateur créé',
            'credentials': {'username': 'admin', 'password': 'admin123'}
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

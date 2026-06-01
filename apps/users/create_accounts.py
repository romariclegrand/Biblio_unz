from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model

User = get_user_model()

@csrf_exempt
def create_accounts(request):
    results = []
    
    # Créer un bibliothécaire
    biblio, created_b = User.objects.get_or_create(
        username='biblio1',
        defaults={
            'email': 'biblio@bibliotheque.com',
            'first_name': 'Jean',
            'last_name': 'Bibliothecaire',
            'role': 'bibliothecaire',
            'is_staff': True
        }
    )
    if created_b:
        biblio.set_password('biblio123')
        biblio.save()
        results.append({'type': 'bibliothecaire', 'username': 'biblio1', 'password': 'biblio123', 'created': True})
    else:
        results.append({'type': 'bibliothecaire', 'username': 'biblio1', 'created': False})
    
    # Créer un étudiant de test
    etudiant, created_e = User.objects.get_or_create(
        username='etudiant1',
        defaults={
            'email': 'etudiant@test.com',
            'first_name': 'Test',
            'last_name': 'Etudiant',
            'role': 'etudiant',
            'ine': '2024TEST12345'
        }
    )
    if created_e:
        etudiant.set_password('etudiant123')
        etudiant.save()
        results.append({'type': 'etudiant', 'username': 'etudiant1', 'password': 'etudiant123', 'created': True})
    else:
        results.append({'type': 'etudiant', 'username': 'etudiant1', 'created': False})
    
    return JsonResponse({'status': 'success', 'accounts': results})

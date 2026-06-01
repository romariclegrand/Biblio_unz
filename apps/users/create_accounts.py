from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model

User = get_user_model()

@csrf_exempt
def create_accounts(request):
    response_text = "<h1>Création des comptes</h1><pre>"
    
    # Créer bibliothécaire
    biblio, created = User.objects.get_or_create(
        username='biblio1',
        defaults={
            'email': 'biblio@bibliotheque.com',
            'first_name': 'Jean',
            'last_name': 'Bibliothecaire',
            'role': 'bibliothecaire',
            'is_staff': True
        }
    )
    if created:
        biblio.set_password('biblio123')
        biblio.save()
        response_text += "✅ Bibliothécaire créé : biblio1 / biblio123\n"
    else:
        response_text += "ℹ️ biblio1 existe déjà\n"
    
    # Créer étudiant
    etudiant, created = User.objects.get_or_create(
        username='etudiant1',
        defaults={
            'email': 'etudiant@test.com',
            'first_name': 'Test',
            'last_name': 'Etudiant',
            'role': 'etudiant',
            'ine': '2024TEST12345'
        }
    )
    if created:
        etudiant.set_password('etudiant123')
        etudiant.save()
        response_text += "✅ Étudiant créé : etudiant1 / etudiant123\n"
    else:
        response_text += "ℹ️ etudiant1 existe déjà\n"
    
    # Lister tous les utilisateurs
    response_text += "\n📋 Liste des comptes :\n"
    for u in User.objects.all():
        response_text += f"   - {u.username} : {u.role}\n"
    
    response_text += "</pre>"
    return HttpResponse(response_text)

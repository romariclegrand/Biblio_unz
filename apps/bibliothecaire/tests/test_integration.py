from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from apps.books.models import Ouvrage, Categorie
from apps.loans.models import Emprunt

User = get_user_model()

class BibliothecaireIntegrationTest(TestCase):
    """Tests d'intégration pour l'application bibliothecaire"""
    
    def setUp(self):
        self.client = Client()
        
        # Créer un bibliothécaire
        self.bibliothecaire = User.objects.create_user(
            username='biblio_test',
            email='biblio@test.com',
            password='pass123',
            role='bibliothecaire',
            is_staff=True
        )
        
        # Créer une catégorie
        self.categorie = Categorie.objects.create(nom='Littérature')
        
        # Créer un ouvrage
        self.ouvrage = Ouvrage.objects.create(
            titre='Test Livre',
            auteur='Test Auteur',
            isbn='1234567890123',
            categorie=self.categorie,
            nombre_exemplaires=2,
            nombre_disponibles=2
        )
        
        # Créer un étudiant
        self.etudiant = User.objects.create_user(
            username='etudiant_biblio',
            email='etudiant@test.com',
            password='pass123',
            role='etudiant'
        )
        
        self.client.login(username='biblio_test', password='pass123')
    
    def test_acces_dashboard_bibliothecaire(self):
        """Test : le bibliothécaire peut accéder à son dashboard"""
        response = self.client.get(reverse('bibliothecaire:dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_acces_gestion_catalogue(self):
        """Test : le bibliothécaire peut accéder à la gestion du catalogue"""
        response = self.client.get(reverse('bibliothecaire:gerer_catalogue'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Livre')
    
    def test_ajouter_nouveau_livre(self):
        """Test : le bibliothécaire peut ajouter un nouveau livre"""
        response = self.client.post(reverse('bibliothecaire:ajouter_livre'), {
            'titre': 'Nouveau Livre',
            'auteur': 'Nouvel Auteur',
            'isbn': '9876543210987',
            'maison_edition': 'Test Edition',
            'annee_edition': '2024',
            'nombre_exemplaires': '3',
            'rayon': 'A1'
        })
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que le livre a été créé
        nouveau_livre = Ouvrage.objects.filter(isbn='9876543210987').first()
        self.assertIsNotNone(nouveau_livre)
        self.assertEqual(nouveau_livre.titre, 'Nouveau Livre')
    
    def test_supprimer_livre_sans_emprunt(self):
        """Test : le bibliothécaire peut supprimer un livre non emprunté"""
        response = self.client.post(reverse('bibliothecaire:supprimer_livre', args=[self.ouvrage.id]))
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que le livre a été supprimé
        with self.assertRaises(Ouvrage.DoesNotExist):
            Ouvrage.objects.get(id=self.ouvrage.id)
    
    def test_acces_gestion_emprunts(self):
        """Test : le bibliothécaire peut accéder à la gestion des emprunts"""
        response = self.client.get(reverse('bibliothecaire:gerer_emprunts'))
        self.assertEqual(response.status_code, 200)
    
    def test_acces_gestion_penalites(self):
        """Test : le bibliothécaire peut accéder à la gestion des pénalités"""
        response = self.client.get(reverse('bibliothecaire:gerer_penalites'))
        self.assertEqual(response.status_code, 200)

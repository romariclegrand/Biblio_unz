from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from apps.books.models import Ouvrage, Categorie
from apps.loans.models import Emprunt
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class AdministrateurIntegrationTest(TestCase):
    """Tests d'intégration pour l'application administrateur"""
    
    def setUp(self):
        self.client = Client()
        
        # Créer un administrateur
        self.admin = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='pass123',
            role='administrateur',
            is_staff=True,
            is_superuser=True
        )
        
        # Créer une catégorie
        self.categorie = Categorie.objects.create(nom='Littérature')
        
        # Créer un ouvrage
        self.ouvrage = Ouvrage.objects.create(
            titre='Livre Test',
            auteur='Auteur Test',
            isbn='1234567890',
            categorie=self.categorie,
            nombre_exemplaires=2,
            nombre_disponibles=2
        )
        
        # Créer un étudiant
        self.etudiant = User.objects.create_user(
            username='etudiant_admin',
            email='etudiant@test.com',
            password='pass123',
            role='etudiant',
            ine='2024ADMIN12345'
        )
        
        self.client.login(username='admin_test', password='pass123')
    
    def test_acces_dashboard_administrateur(self):
        """Test : l'administrateur peut accéder à son dashboard"""
        response = self.client.get(reverse('administrateur:dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_acces_gestion_utilisateurs(self):
        """Test : l'administrateur peut accéder à la gestion des utilisateurs"""
        response = self.client.get(reverse('administrateur:gerer_utilisateurs'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'etudiant_admin')
    
    def test_ajouter_nouvel_utilisateur(self):
        """Test : l'administrateur peut créer un nouvel utilisateur"""
        response = self.client.post(reverse('administrateur:ajouter_utilisateur'), {
            'username': 'nouveau_user',
            'email': 'nouveau@test.com',
            'password': 'pass123',
            'first_name': 'Jean',
            'last_name': 'Nouveau',
            'role': 'etudiant',
            'ine': '2025TEST12345'
        })
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que l'utilisateur a été créé
        self.assertTrue(User.objects.filter(username='nouveau_user').exists())
    
    def test_acces_statistiques(self):
        """Test : l'administrateur peut accéder aux statistiques"""
        response = self.client.get(reverse('administrateur:statistiques'))
        self.assertEqual(response.status_code, 200)
    
    def test_acces_logs(self):
        """Test : l'administrateur peut accéder aux journaux d'activité"""
        response = self.client.get(reverse('administrateur:logs'))
        self.assertEqual(response.status_code, 200)
    
    def test_acces_configuration_systeme(self):
        """Test : l'administrateur peut accéder à la configuration système"""
        response = self.client.get(reverse('administrateur:configurer_systeme'))
        self.assertEqual(response.status_code, 200)
    
    def test_modifier_configuration_systeme(self):
        """Test : l'administrateur peut modifier la configuration système"""
        response = self.client.post(reverse('administrateur:configurer_systeme'), {
            'duree_emprunt_jours': '14',
            'tarif_penalite_journalier': '200'
        })
        self.assertEqual(response.status_code, 302)
        
        from apps.statistics.models import ConfigurationSysteme
        config = ConfigurationSysteme.get_config()
        self.assertEqual(config.duree_emprunt_jours, 14)
        self.assertEqual(config.tarif_penalite_journalier, 200)

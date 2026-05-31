from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class UsersIntegrationTest(TestCase):
    """Tests d'intégration pour l'application users"""
    
    def setUp(self):
        """Configuration initiale avant chaque test"""
        self.client = Client()
        self.user_data = {
            'username': 'testetudiant',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Jean',
            'last_name': 'Dupont',
            'ine': '2024INFO12345'
        }
    
    def test_inscription_etudiant_avec_ine(self):
        """Test : un étudiant peut s'inscrire avec un INE valide (12 caractères)"""
        response = self.client.post(reverse('users:register'), {
            'username': 'nouvel_etudiant',
            'email': 'nouveau@example.com',
            'password': 'motdepasse123',
            'password2': 'motdepasse123',
            'nom': 'Martin',
            'prenom': 'Sophie',
            'ine': '2025INFO67890'
        })
        # Vérifier la redirection après inscription
        self.assertEqual(response.status_code, 302)
        # Vérifier que l'utilisateur a été créé
        self.assertTrue(User.objects.filter(username='nouvel_etudiant').exists())
    
    def test_inscription_avec_ine_invalide(self):
        """Test : l'inscription échoue si l'INE n'a pas 12 caractères"""
        response = self.client.post(reverse('users:register'), {
            'username': 'etudiant_ine_invalide',
            'email': 'invalide@example.com',
            'password': 'motdepasse123',
            'password2': 'motdepasse123',
            'nom': 'Durand',
            'prenom': 'Paul',
            'ine': '123'  # INE trop court (3 caractères au lieu de 12)
        })
        # Vérifier que le formulaire est réaffiché avec une erreur
        self.assertEqual(response.status_code, 200)
        # Vérifier que l'utilisateur n'a PAS été créé
        self.assertFalse(User.objects.filter(username='etudiant_ine_invalide').exists())
    
    def test_connexion_utilisateur_existant(self):
        """Test : un utilisateur existant peut se connecter"""
        # Créer un utilisateur
        user = User.objects.create_user(
            username='utilisateur_test',
            email='test@example.com',
            password='bonmotdepasse',
            role='etudiant'
        )
        
        # Tenter la connexion
        response = self.client.post(reverse('users:login'), {
            'username': 'utilisateur_test',
            'password': 'bonmotdepasse'
        })
        
        # Vérifier la redirection vers le dashboard étudiant
        self.assertEqual(response.status_code, 302)
    
    def test_connexion_mot_de_passe_incorrect(self):
        """Test : la connexion échoue avec un mot de passe incorrect"""
        user = User.objects.create_user(
            username='utilisateur_test2',
            email='test2@example.com',
            password='bonmotdepasse',
            role='etudiant'
        )
        
        response = self.client.post(reverse('users:login'), {
            'username': 'utilisateur_test2',
            'password': 'mauvais_mot_de_passe'
        })
        
        # Vérifier que le formulaire est réaffiché (200) et pas de redirection
        self.assertEqual(response.status_code, 200)
    
    def test_acces_dashboard_selon_role_etudiant(self):
        """Test : un étudiant est redirigé vers le dashboard étudiant"""
        user = User.objects.create_user(
            username='etudiant_role',
            email='etudiant@example.com',
            password='pass123',
            role='etudiant'
        )
        self.client.login(username='etudiant_role', password='pass123')
        
        response = self.client.get(reverse('users:dashboard_etudiant'))
        self.assertEqual(response.status_code, 200)
    
    def test_acces_profil_utilisateur_connecte(self):
        """Test : un utilisateur connecté peut accéder à son profil"""
        user = User.objects.create_user(
            username='profil_test',
            email='profil@example.com',
            password='pass123',
            role='etudiant'
        )
        self.client.login(username='profil_test', password='pass123')
        
        response = self.client.get(reverse('users:profil'))
        self.assertEqual(response.status_code, 200)
    
    def test_ine_unique_par_etudiant(self):
        """Test : deux étudiants ne peuvent pas avoir le même INE"""
        User.objects.create_user(
            username='premier',
            email='premier@example.com',
            password='pass123',
            ine='123456789012',
            role='etudiant'
        )
        
        response = self.client.post(reverse('users:register'), {
            'username': 'second',
            'email': 'second@example.com',
            'password': 'pass123',
            'password2': 'pass123',
            'nom': 'Deuxieme',
            'prenom': 'User',
            'ine': '123456789012'  # Même INE
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cet INE est déjà associé à un compte")

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from apps.books.models import Ouvrage, Categorie

User = get_user_model()

class BooksIntegrationTest(TestCase):
    """Tests d'intégration pour l'application books"""
    
    def setUp(self):
        self.client = Client()
        
        # Créer une catégorie
        self.categorie = Categorie.objects.create(nom='Littérature')
        
        # Créer un ouvrage
        self.ouvrage = Ouvrage.objects.create(
            titre='Le Petit Prince',
            auteur='Saint-Exupéry',
            isbn='9782070612758',
            categorie=self.categorie,
            nombre_exemplaires=3,
            nombre_disponibles=3,
            maison_edition='Gallimard',
            annee_edition=1943
        )
        
        # Créer un étudiant pour les tests
        self.etudiant = User.objects.create_user(
            username='etudiant_test',
            email='etudiant@test.com',
            password='pass123',
            role='etudiant'
        )
    
    def test_affichage_catalogue(self):
        """Test : le catalogue affiche la liste des ouvrages"""
        response = self.client.get(reverse('books:catalogue'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Le Petit Prince')
        self.assertContains(response, 'Saint-Exupéry')
    
    def test_recherche_ouvrage_par_titre(self):
        """Test : la recherche par titre fonctionne"""
        response = self.client.get(reverse('books:catalogue'), {'recherche': 'Petit'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Le Petit Prince')
    
    def test_recherche_ouvrage_par_auteur(self):
        """Test : la recherche par auteur fonctionne"""
        response = self.client.get(reverse('books:catalogue'), {'recherche': 'Saint-Exupéry'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Le Petit Prince')
    
    def test_filtrage_par_categorie(self):
        """Test : le filtrage par catégorie fonctionne"""
        response = self.client.get(reverse('books:catalogue'), {'categorie': self.categorie.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Le Petit Prince')
    
    def test_detail_ouvrage(self):
        """Test : la page de détail d'un ouvrage s'affiche correctement"""
        response = self.client.get(reverse('books:livre_detail', args=[self.ouvrage.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Le Petit Prince')
        self.assertContains(response, 'Saint-Exupéry')
        self.assertContains(response, 'Gallimard')
        self.assertContains(response, '1943')
    
    def test_isbn_unique(self):
        """Test : deux ouvrages ne peuvent pas avoir le même ISBN"""
        with self.assertRaises(Exception):
            Ouvrage.objects.create(
                titre='Autre livre',
                auteur='Autre auteur',
                isbn='9782070612758',  # Même ISBN
                nombre_exemplaires=1,
                nombre_disponibles=1
            )

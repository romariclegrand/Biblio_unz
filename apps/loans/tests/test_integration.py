from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from apps.books.models import Ouvrage, Categorie
from apps.loans.models import Emprunt, Reservation

User = get_user_model()

class LoansIntegrationTest(TestCase):
    """Tests d'intégration pour l'application loans"""
    
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
            nombre_exemplaires=2,
            nombre_disponibles=2
        )
        
        # Créer un étudiant
        self.etudiant = User.objects.create_user(
            username='etudiant_loan',
            email='etudiant@test.com',
            password='pass123',
            role='etudiant',
            ine='2024LOAN12345'
        )
        
        self.client.login(username='etudiant_loan', password='pass123')
    
    def test_emprunter_ouvrage_disponible(self):
        """Test : un étudiant peut emprunter un ouvrage disponible"""
        response = self.client.post(reverse('loans:emprunter', args=[self.ouvrage.id]))
        
        # Vérifier la redirection
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que l'emprunt a été créé
        emprunt = Emprunt.objects.filter(etudiant=self.etudiant, ouvrage=self.ouvrage).first()
        self.assertIsNotNone(emprunt)
        
        # Vérifier que le stock a diminué
        self.ouvrage.refresh_from_db()
        self.assertEqual(self.ouvrage.nombre_disponibles, 1)
    
    def test_emprunter_ouvrage_deja_emprunte(self):
        """Test : un étudiant ne peut pas emprunter le même ouvrage deux fois"""
        # Premier emprunt
        self.client.post(reverse('loans:emprunter', args=[self.ouvrage.id]))
        
        # Deuxième tentative
        response = self.client.post(reverse('loans:emprunter', args=[self.ouvrage.id]))
        
        # Vérifier le message d'erreur
        self.assertEqual(response.status_code, 302)
    
    def test_consulter_mes_emprunts(self):
        """Test : l'étudiant peut consulter la liste de ses emprunts"""
        # Créer un emprunt
        Emprunt.objects.create(
            etudiant=self.etudiant,
            ouvrage=self.ouvrage,
            date_retour_prevue=timezone.now() + timedelta(days=7)
        )
        
        response = self.client.get(reverse('loans:mes_emprunts'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Le Petit Prince')
    
    def test_reserver_ouvrage_indisponible(self):
        """Test : un étudiant peut réserver un ouvrage quand tous les exemplaires sont empruntés"""
        # Épuiser le stock
        self.ouvrage.nombre_disponibles = 0
        self.ouvrage.save()
        
        response = self.client.post(reverse('loans:reserver', args=[self.ouvrage.id]))
        self.assertEqual(response.status_code, 302)
        
        # Vérifier que la réservation a été créée
        reservation = Reservation.objects.filter(etudiant=self.etudiant, ouvrage=self.ouvrage).first()
        self.assertIsNotNone(reservation)
    
    def test_reserver_ouvrage_deja_reserve(self):
        """Test : un étudiant ne peut pas réserver deux fois le même ouvrage"""
        # Épuiser le stock
        self.ouvrage.nombre_disponibles = 0
        self.ouvrage.save()
        
        # Première réservation
        self.client.post(reverse('loans:reserver', args=[self.ouvrage.id]))
        
        # Deuxième tentative
        response = self.client.post(reverse('loans:reserver', args=[self.ouvrage.id]))
        self.assertEqual(response.status_code, 302)
        
        # Vérifier qu'une seule réservation existe
        reservations = Reservation.objects.filter(etudiant=self.etudiant, ouvrage=self.ouvrage)
        self.assertEqual(reservations.count(), 1)
    
    def test_consulter_mes_reservations(self):
        """Test : l'étudiant peut consulter la liste de ses réservations"""
        # Épuiser le stock et créer une réservation
        self.ouvrage.nombre_disponibles = 0
        self.ouvrage.save()
        
        Reservation.objects.create(
            etudiant=self.etudiant,
            ouvrage=self.ouvrage,
            date_expiration=timezone.now() + timedelta(hours=48)
        )
        
        response = self.client.get(reverse('loans:mes_reservations'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Le Petit Prince')

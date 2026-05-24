from django.db import models
from django.utils import timezone
from datetime import timedelta
from apps.users.models import Utilisateur
from apps.books.models import Ouvrage

class Emprunt(models.Model):
    STATUT_CHOICES = [
        ('en_cours', 'En cours'),
        ('retourne', 'Retourné'),
        ('en_retard', 'En retard'),
    ]
    
    etudiant = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='emprunts')
    ouvrage = models.ForeignKey(Ouvrage, on_delete=models.CASCADE, related_name='emprunts')
    date_emprunt = models.DateTimeField(auto_now_add=True)
    date_retour_prevue = models.DateTimeField()
    date_retour_reelle = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_cours')
    
    def save(self, *args, **kwargs):
        if not self.date_retour_prevue:
            self.date_retour_prevue = timezone.now() + timedelta(days=7)
        # Mettre à jour le statut automatiquement
        if self.date_retour_reelle:
            self.statut = 'retourne'
        elif timezone.now() > self.date_retour_prevue:
            self.statut = 'en_retard'
        else:
            self.statut = 'en_cours'
        super().save(*args, **kwargs)
    
    def retourner(self):
        self.date_retour_reelle = timezone.now()
        self.ouvrage.nombre_disponibles += 1
        self.ouvrage.save()
        self.save()
    
    def __str__(self):
        return f"{self.etudiant.get_full_name()} - {self.ouvrage.titre}"
    
    class Meta:
        ordering = ['-date_emprunt']

class Penalite(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('payee', 'Payée'),
        ('annulee', 'Annulée'),
    ]
    
    emprunt = models.OneToOneField(Emprunt, on_delete=models.CASCADE, related_name='penalite')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    jours_retard = models.IntegerField()
    date_calcul = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    motif_annulation = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Pénalité {self.emprunt.etudiant.get_full_name()} - {self.montant} FCFA"
    
    class Meta:
        ordering = ['-date_calcul']

class Reservation(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('notifie', 'Notifié'),
        ('expiree', 'Expirée'),
        ('annulee', 'Annulée'),
    ]
    
    ouvrage = models.ForeignKey(Ouvrage, on_delete=models.CASCADE, related_name='reservations')
    etudiant = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='reservations')
    date_reservation = models.DateTimeField(auto_now_add=True)
    date_expiration = models.DateTimeField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_notification = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.date_expiration:
            self.date_expiration = timezone.now() + timedelta(hours=48)
        super().save(*args, **kwargs)
    
    def est_expiree(self):
        return timezone.now() > self.date_expiration and self.statut == 'en_attente'
    
    def notifier(self):
        self.statut = 'notifie'
        self.date_notification = timezone.now()
        self.save()
    
    def __str__(self):
        return f"{self.etudiant.get_full_name()} - {self.ouvrage.titre} ({self.statut})"
    
    class Meta:
        ordering = ['date_reservation']

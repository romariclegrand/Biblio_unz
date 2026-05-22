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

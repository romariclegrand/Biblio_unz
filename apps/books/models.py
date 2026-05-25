from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    rayon = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.nom
    
    class Meta:
        ordering = ['nom']

class Ouvrage(models.Model):
    titre = models.CharField(max_length=200)
    auteur = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, blank=True)
    maison_edition = models.CharField(max_length=100, blank=True, null=True, verbose_name="Maison d'édition")
    annee_edition = models.IntegerField(blank=True, null=True, verbose_name="Année d'édition")
    nombre_exemplaires = models.IntegerField(default=1)
    nombre_disponibles = models.IntegerField(default=1)
    rayon = models.CharField(max_length=100, blank=True, null=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.titre} - {self.auteur}"
    
    def est_disponible(self):
        return self.nombre_disponibles > 0
    
    class Meta:
        ordering = ['titre']

class HistoriqueOuvrage(models.Model):
    ACTION_CHOICES = [
        ('create', 'Création'),
        ('update', 'Modification'),
        ('delete', 'Suppression'),
    ]
    ouvrage = models.ForeignKey(Ouvrage, on_delete=models.CASCADE, related_name='historiques')
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    details = models.TextField(blank=True, null=True)
    date_action = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.ouvrage.titre}"
    
    class Meta:
        ordering = ['-date_action']

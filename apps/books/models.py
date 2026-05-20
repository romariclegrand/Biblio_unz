from django.db import models
from django.core.exceptions import ValidationError

class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.nom
    
    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

class Ouvrage(models.Model):
    titre = models.CharField(max_length=200)
    auteur = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True, help_text="Code ISBN à 13 chiffres")
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, blank=True)
    editeur = models.CharField(max_length=100, blank=True, null=True)
    annee_publication = models.IntegerField(blank=True, null=True)
    nombre_exemplaires = models.IntegerField(default=1)
    nombre_disponibles = models.IntegerField(default=1)
    date_ajout = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.titre} - {self.auteur} ({self.isbn})"
    
    def clean(self):
        if self.nombre_disponibles > self.nombre_exemplaires:
            raise ValidationError("Le nombre de disponibles ne peut pas dépasser le nombre total d'exemplaires.")
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Nouvel ouvrage
            self.nombre_disponibles = self.nombre_exemplaires
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Ouvrage"
        verbose_name_plural = "Ouvrages"
        ordering = ['titre']

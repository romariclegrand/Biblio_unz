from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError

def validate_ine(value):
    if len(value) != 12:
        raise ValidationError("L'INE doit contenir exactement 12 caractères.")
    if not value.isalnum():
        raise ValidationError("L'INE ne doit contenir que des lettres et chiffres.")

class Utilisateur(AbstractUser):
    ROLE_CHOICES = (
        ('etudiant', 'Étudiant'),
        ('bibliothecaire', 'Bibliothécaire'),
        ('administrateur', 'Administrateur'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='etudiant')
    telephone = models.CharField(max_length=15, blank=True, null=True)
    actif = models.BooleanField(default=True)
    ine = models.CharField(max_length=12, unique=True, null=True, blank=True, validators=[validate_ine])
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def est_etudiant(self):
        return self.role == 'etudiant'
    
    def est_bibliothecaire(self):
        return self.role == 'bibliothecaire'
    
    def est_administrateur(self):
        return self.role == 'administrateur'

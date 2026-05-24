from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class LogActivite(models.Model):
    ACTION_CHOICES = [
        ('connexion', 'Connexion'),
        ('deconnexion', 'Déconnexion'),
        ('creation', 'Création'),
        ('modification', 'Modification'),
        ('suppression', 'Suppression'),
        ('emprunt', 'Emprunt'),
        ('retour', 'Retour'),
        ('penalite', 'Pénalité'),
    ]
    
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='logs')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    details = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    date_action = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.utilisateur} - {self.get_action_display()} - {self.date_action.strftime('%d/%m/%Y %H:%M')}"
    
    class Meta:
        ordering = ['-date_action']
        verbose_name = "Journal d'activité"
        verbose_name_plural = "Journaux d'activité"

class ConfigurationSysteme(models.Model):
    duree_emprunt_jours = models.IntegerField(default=7, help_text="Durée d'emprunt par défaut en jours")
    tarif_penalite_journalier = models.IntegerField(default=100, help_text="Tarif journalier de pénalité en FCFA")
    date_modification = models.DateTimeField(auto_now=True)
    modifie_par = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"Configuration du {self.date_modification.strftime('%d/%m/%Y')}"
    
    class Meta:
        verbose_name = "Configuration du système"
        verbose_name_plural = "Configurations du système"
        
    @classmethod
    def get_config(cls):
        """Récupère la configuration active (la première ou en crée une par défaut)"""
        config = cls.objects.first()
        if not config:
            config = cls.objects.create()
        return config

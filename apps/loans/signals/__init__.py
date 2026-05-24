from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from ..models import Emprunt, Penalite, Reservation

# Variables globales pour la configuration
_config_duree_emprunt = 7
_config_tarif_penalite = 100

def update_config(duree, tarif):
    global _config_duree_emprunt, _config_tarif_penalite
    _config_duree_emprunt = duree
    _config_tarif_penalite = tarif

@receiver(post_save, sender=Emprunt)
def calculer_penalite(sender, instance, created, **kwargs):
    if instance.statut == 'en_retard' and not instance.date_retour_reelle:
        jours_retard = (timezone.now() - instance.date_retour_prevue).days
        if jours_retard > 0:
            montant = jours_retard * _config_tarif_penalite
            
            penalite, created = Penalite.objects.get_or_create(
                emprunt=instance,
                defaults={
                    'montant': montant,
                    'jours_retard': jours_retard,
                    'statut': 'active'
                }
            )
            if not created and penalite.statut == 'active':
                penalite.montant = montant
                penalite.jours_retard = jours_retard
                penalite.save()

@receiver(post_save, sender=Emprunt)
def gerer_file_attente(sender, instance, **kwargs):
    """Quand un livre est retourné, notifier le prochain réservé"""
    if instance.date_retour_reelle and instance.statut == 'retourne':
        prochaine_reservation = Reservation.objects.filter(
            ouvrage=instance.ouvrage,
            statut='en_attente'
        ).order_by('date_reservation').first()
        
        if prochaine_reservation:
            try:
                send_mail(
                    "Livre disponible - Biblio_UNZ",
                    f"Bonjour {prochaine_reservation.etudiant.first_name},\n\n"
                    f"Le livre '{instance.ouvrage.titre}' que vous avez réservé est maintenant disponible.\n"
                    f"Vous avez 48h pour venir l'emprunter.\n\n"
                    f"Cordialement,\nL'équipe Biblio_UNZ",
                    settings.DEFAULT_FROM_EMAIL,
                    [prochaine_reservation.etudiant.email],
                    fail_silently=False,
                )
                prochaine_reservation.notifier()
            except:
                pass

def verifier_reservations_expirees():
    """À exécuter par cron job"""
    reservations_expirees = Reservation.objects.filter(
        statut='en_attente',
        date_expiration__lte=timezone.now()
    )
    for reservation in reservations_expirees:
        reservation.statut = 'expiree'
        reservation.save()

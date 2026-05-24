from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from apps.loans.models import Emprunt

class Command(BaseCommand):
    help = 'Envoyer des rappels aux étudiants pour les retours proches'
    
    def handle(self, *args, **kwargs):
        today = timezone.now()
        
        # Rappel 3 jours avant
        date_rappel_3j = today + timedelta(days=3)
        emprunts_3j = Emprunt.objects.filter(
            date_retour_prevue__date=date_rappel_3j.date(),
            statut='en_cours'
        )
        
        for emprunt in emprunts_3j:
            self.envoyer_email(
                emprunt,
                "Rappel : retour dans 3 jours",
                f"Le livre '{emprunt.ouvrage.titre}' doit être retourné dans 3 jours (le {emprunt.date_retour_prevue.strftime('%d/%m/%Y')})."
            )
        
        # Rappel le jour J
        emprunts_jour = Emprunt.objects.filter(
            date_retour_prevue__date=today.date(),
            statut='en_cours'
        )
        
        for emprunt in emprunts_jour:
            self.envoyer_email(
                emprunt,
                "Dernier jour pour retourner votre livre",
                f"Le livre '{emprunt.ouvrage.titre}' doit être retourné aujourd'hui {emprunt.date_retour_prevue.strftime('%d/%m/%Y')}. Passé ce délai, une pénalité s'appliquera."
            )
        
        self.stdout.write(self.style.SUCCESS(f"Rappels envoyés : {emprunts_3j.count() + emprunts_jour.count()}"))
    
    def envoyer_email(self, emprunt, sujet, message):
        try:
            send_mail(
                f"Biblio_UNZ - {sujet}",
                f"Bonjour {emprunt.etudiant.first_name} {emprunt.etudiant.last_name},\n\n{message}\n\nCordialement,\nL'équipe Biblio_UNZ",
                settings.DEFAULT_FROM_EMAIL,
                [emprunt.etudiant.email],
                fail_silently=False,
            )
            self.stdout.write(f"Email envoyé à {emprunt.etudiant.email}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erreur pour {emprunt.etudiant.email}: {e}"))

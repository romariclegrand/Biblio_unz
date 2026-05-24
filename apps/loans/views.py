from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from apps.books.models import Ouvrage
from apps.statistics.models import ConfigurationSysteme
from .models import Emprunt, Reservation

class EmprunterView(LoginRequiredMixin, View):
    def post(self, request, livre_id):
        livre = get_object_or_404(Ouvrage, id=livre_id)
        
        if request.user.role != 'etudiant':
            messages.error(request, "Seuls les étudiants peuvent emprunter.")
            return redirect('books:livre_detail', livre_id=livre.id)
        
        if Emprunt.objects.filter(etudiant=request.user, ouvrage=livre, statut__in=['en_cours', 'en_retard']).exists():
            messages.error(request, f"Vous avez déjà emprunté '{livre.titre}'. Retournez-le d'abord.")
            return redirect('books:livre_detail', livre_id=livre.id)
        
        if livre.nombre_disponibles <= 0:
            messages.error(request, "Ce livre n'est pas disponible.")
            return redirect('books:livre_detail', livre_id=livre.id)
        
        # Récupérer la configuration système
        config = ConfigurationSysteme.get_config()
        duree_emprunt = config.duree_emprunt_jours
        
        emprunt = Emprunt.objects.create(
            etudiant=request.user,
            ouvrage=livre,
            date_retour_prevue=timezone.now() + timedelta(days=duree_emprunt)
        )
        
        livre.nombre_disponibles -= 1
        livre.save()
        
        try:
            send_mail(
                "Confirmation d'emprunt - Biblio_UNZ",
                f"Bonjour {request.user.first_name},\n\n"
                f"Vous avez emprunté '{livre.titre}'.\n"
                f"Date de retour prévue: {emprunt.date_retour_prevue.strftime('%d/%m/%Y')}\n\n"
                f"Merci !",
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                fail_silently=False,
            )
        except:
            pass
        
        messages.success(request, f"Emprunté '{livre.titre}'. Retour prévu le {emprunt.date_retour_prevue.strftime('%d/%m/%Y')}")
        return redirect('books:livre_detail', livre_id=livre.id)

class MesEmpruntsView(LoginRequiredMixin, View):
    def get(self, request):
        emprunts = Emprunt.objects.filter(etudiant=request.user)
        return render(request, 'loans/mes_emprunts.html', {'emprunts': emprunts})

class ReserverOuvrageView(LoginRequiredMixin, View):
    def post(self, request, livre_id):
        livre = get_object_or_404(Ouvrage, id=livre_id)
        
        if request.user.role != 'etudiant':
            messages.error(request, "Seuls les étudiants peuvent réserver.")
            return redirect('books:livre_detail', livre_id=livre.id)
        
        if Reservation.objects.filter(ouvrage=livre, etudiant=request.user, statut='en_attente').exists():
            messages.warning(request, "Vous avez déjà une réservation en attente pour ce livre.")
            return redirect('books:livre_detail', livre_id=livre.id)
        
        if Emprunt.objects.filter(ouvrage=livre, etudiant=request.user, statut__in=['en_cours', 'en_retard']).exists():
            messages.warning(request, "Vous avez déjà emprunté ce livre.")
            return redirect('books:livre_detail', livre_id=livre.id)
        
        reservation = Reservation.objects.create(
            ouvrage=livre,
            etudiant=request.user,
            date_expiration=timezone.now() + timedelta(hours=48)
        )
        
        try:
            send_mail(
                "Confirmation de réservation - Biblio_UNZ",
                f"Bonjour {request.user.first_name},\n\n"
                f"Vous avez réservé '{livre.titre}'.\n"
                f"Vous serez notifié dès qu'un exemplaire sera disponible.\n"
                f"Cette réservation expire le {reservation.date_expiration.strftime('%d/%m/%Y à %H:%M')}.\n\n"
                f"Cordialement,\nL'équipe Biblio_UNZ",
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                fail_silently=False,
            )
        except:
            pass
        
        messages.success(request, f"Réservation effectuée pour '{livre.titre}'. Vous serez notifié dès disponibilité.")
        return redirect('books:livre_detail', livre_id=livre.id)

class MesReservationsView(LoginRequiredMixin, View):
    def get(self, request):
        reservations = Reservation.objects.filter(etudiant=request.user)
        for res in reservations:
            if res.est_expiree():
                res.statut = 'expiree'
                res.save()
        return render(request, 'loans/mes_reservations.html', {'reservations': reservations})

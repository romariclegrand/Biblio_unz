from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from apps.books.models import Ouvrage
from .models import Emprunt

class EmprunterView(LoginRequiredMixin, View):
    def post(self, request, livre_id):
        livre = get_object_or_404(Ouvrage, id=livre_id)
        
        if request.user.role != 'etudiant':
            messages.error(request, "Seuls les étudiants peuvent emprunter.")
            return redirect('books:livre_detail', livre_id=livre.id)
        
        # Vérifier si déjà emprunté non retourné
        if Emprunt.objects.filter(etudiant=request.user, ouvrage=livre, statut__in=['en_cours', 'en_retard']).exists():
            messages.error(request, f"Vous avez déjà emprunté '{livre.titre}'. Retournez-le d'abord.")
            return redirect('books:livre_detail', livre_id=livre.id)
        
        if livre.nombre_disponibles <= 0:
            messages.error(request, "Ce livre n'est pas disponible.")
            return redirect('books:livre_detail', livre_id=livre.id)
        
        # Créer l'emprunt
        emprunt = Emprunt.objects.create(
            etudiant=request.user,
            ouvrage=livre,
            date_retour_prevue=timezone.now() + timedelta(days=7)
        )
        
        # Mettre à jour le stock
        livre.nombre_disponibles -= 1
        livre.save()
        
        # Email de confirmation
        try:
            send_mail(
                "Confirmation d'emprunt - Biblio_UNZ",
                f"Bonjour {request.user.first_name},\n\nVous avez emprunté '{livre.titre}'.\nDate de retour prévue: {emprunt.date_retour_prevue.strftime('%d/%m/%Y')}\n\nMerci !",
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

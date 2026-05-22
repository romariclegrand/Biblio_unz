from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from apps.books.models import Ouvrage, Categorie, HistoriqueOuvrage
from apps.loans.models import Emprunt
from apps.users.models import Utilisateur

# ==================== DASHBOARD ====================
class DashboardBibliothecaireView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'bibliothecaire':
            messages.error(request, "Accès réservé aux bibliothécaires.")
            return redirect('users:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        stats = {
            'total_livres': Ouvrage.objects.count(),
            'livres_disponibles': Ouvrage.objects.filter(nombre_disponibles__gt=0).count(),
            'emprunts_en_cours': Emprunt.objects.filter(statut='en_cours').count(),
            'emprunts_retard': Emprunt.objects.filter(statut='en_retard').count(),
        }
        return render(request, 'bibliothecaire/dashboard.html', {'stats': stats, 'user': request.user})

# ==================== GESTION DU CATALOGUE ====================
class GererCatalogueView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'bibliothecaire':
            return redirect('users:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        livres = Ouvrage.objects.all()
        return render(request, 'bibliothecaire/gerer_catalogue.html', {'livres': livres})

class AjouterLivreView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'bibliothecaire':
            return redirect('users:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        categories = Categorie.objects.all()
        return render(request, 'bibliothecaire/ajouter_livre.html', {'categories': categories})
    
    def post(self, request):
        titre = request.POST.get('titre')
        auteur = request.POST.get('auteur')
        isbn = request.POST.get('isbn')
        categorie_id = request.POST.get('categorie')
        nombre_exemplaires = request.POST.get('nombre_exemplaires')
        rayon = request.POST.get('rayon')
        
        # Validation
        if not titre or not auteur or not isbn:
            messages.error(request, "Titre, auteur et ISBN sont obligatoires.")
            return redirect('bibliothecaire:ajouter_livre')
        
        if Ouvrage.objects.filter(isbn=isbn).exists():
            messages.error(request, "Cet ISBN existe déjà.")
            return redirect('bibliothecaire:ajouter_livre')
        
        livre = Ouvrage.objects.create(
            titre=titre,
            auteur=auteur,
            isbn=isbn,
            categorie_id=categorie_id if categorie_id else None,
            nombre_exemplaires=int(nombre_exemplaires),
            nombre_disponibles=int(nombre_exemplaires),
            rayon=rayon
        )
        
        # Historique
        HistoriqueOuvrage.objects.create(
            ouvrage=livre,
            utilisateur=request.user,
            action='create',
            details=f"Ajout du livre : {titre}"
        )
        
        messages.success(request, f"Livre '{titre}' ajouté avec succès.")
        return redirect('bibliothecaire:gerer_catalogue')

class ModifierLivreView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'bibliothecaire':
            return redirect('users:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, livre_id):
        livre = get_object_or_404(Ouvrage, id=livre_id)
        categories = Categorie.objects.all()
        return render(request, 'bibliothecaire/modifier_livre.html', {'livre': livre, 'categories': categories})
    
    def post(self, request, livre_id):
        livre = get_object_or_404(Ouvrage, id=livre_id)
        
        ancien_titre = livre.titre
        livre.titre = request.POST.get('titre')
        livre.auteur = request.POST.get('auteur')
        livre.isbn = request.POST.get('isbn')
        livre.categorie_id = request.POST.get('categorie')
        livre.nombre_exemplaires = int(request.POST.get('nombre_exemplaires'))
        livre.rayon = request.POST.get('rayon')
        
        # Ajuster le nombre de disponibles
        difference = livre.nombre_exemplaires - livre.nombre_disponibles
        if difference > 0:
            livre.nombre_disponibles += difference
        
        livre.save()
        
        HistoriqueOuvrage.objects.create(
            ouvrage=livre,
            utilisateur=request.user,
            action='update',
            details=f"Modification du livre : {ancien_titre} -> {livre.titre}"
        )
        
        messages.success(request, f"Livre '{livre.titre}' modifié avec succès.")
        return redirect('bibliothecaire:gerer_catalogue')

class SupprimerLivreView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'bibliothecaire':
            return redirect('users:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, livre_id):
        livre = get_object_or_404(Ouvrage, id=livre_id)
        
        # Vérifier si des exemplaires sont empruntés
        emprunts_actifs = Emprunt.objects.filter(ouvrage=livre, statut__in=['en_cours', 'en_retard']).exists()
        if emprunts_actifs:
            messages.error(request, "Impossible de supprimer : des exemplaires sont actuellement empruntés.")
            return redirect('bibliothecaire:gerer_catalogue')
        
        titre = livre.titre
        HistoriqueOuvrage.objects.create(
            ouvrage=livre,
            utilisateur=request.user,
            action='delete',
            details=f"Suppression du livre : {titre}"
        )
        livre.delete()
        messages.success(request, f"Livre '{titre}' supprimé avec succès.")
        return redirect('bibliothecaire:gerer_catalogue')

# ==================== GESTION DES EMPRUNTS ====================
class GererEmpruntsView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'bibliothecaire':
            return redirect('users:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        statut_filtre = request.GET.get('statut', '')
        emprunts = Emprunt.objects.all()
        
        if statut_filtre:
            emprunts = emprunts.filter(statut=statut_filtre)
        
        return render(request, 'bibliothecaire/gerer_emprunts.html', {
            'emprunts': emprunts,
            'statut_filtre': statut_filtre
        })

class EnregistrerRetourView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'bibliothecaire':
            return redirect('users:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, emprunt_id):
        emprunt = get_object_or_404(Emprunt, id=emprunt_id)
        if emprunt.statut != 'retourne':
            emprunt.retourner()
            messages.success(request, f"Retour enregistré : {emprunt.ouvrage.titre}")
        return redirect('bibliothecaire:gerer_emprunts')

class EnvoyerRappelView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'bibliothecaire':
            return redirect('users:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, emprunt_id):
        emprunt = get_object_or_404(Emprunt, id=emprunt_id)
        try:
            send_mail(
                "Rappel de retour - Biblio_UNZ",
                f"Bonjour {emprunt.etudiant.get_full_name()},\n\nLe livre '{emprunt.ouvrage.titre}' est en retard.\nMerci de le retourner rapidement.",
                settings.DEFAULT_FROM_EMAIL,
                [emprunt.etudiant.email],
                fail_silently=False,
            )
            messages.success(request, f"Rappel envoyé à {emprunt.etudiant.email}")
        except:
            messages.error(request, "Erreur lors de l'envoi")
        return redirect('bibliothecaire:gerer_emprunts')

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
import csv
from apps.users.models import Utilisateur
from apps.books.models import Ouvrage
from apps.loans.models import Emprunt

User = get_user_model()

# ==================== DASHBOARD ====================
class DashboardAdminView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'administrateur':
            messages.error(request, "Accès réservé aux administrateurs.")
            return redirect('users:dashboard_etudiant')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        stats = {
            'etudiants': Utilisateur.objects.filter(role='etudiant').count(),
            'bibliothecaires': Utilisateur.objects.filter(role='bibliothecaire').count(),
            'livres': Ouvrage.objects.count(),
            'emprunts': Emprunt.objects.count(),
            'retards': Emprunt.objects.filter(statut='en_retard').count(),
        }
        return render(request, 'administrateur/dashboard.html', {'stats': stats})

# ==================== GESTION DES UTILISATEURS ====================
class GererUtilisateursView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'administrateur':
            return redirect('users:dashboard_etudiant')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        utilisateurs = Utilisateur.objects.all()
        return render(request, 'administrateur/gerer_utilisateurs.html', {'utilisateurs': utilisateurs})

class AjouterUtilisateurView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'administrateur':
            return redirect('users:dashboard_etudiant')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        return render(request, 'administrateur/ajouter_utilisateur.html')
    
    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        ine = request.POST.get('ine')
        
        if Utilisateur.objects.filter(username=username).exists():
            messages.error(request, "Nom d'utilisateur déjà pris")
            return redirect('administrateur:ajouter_utilisateur')
        
        user = Utilisateur.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            ine=ine if role == 'etudiant' else None
        )
        
        messages.success(request, f"Utilisateur {username} créé avec succès")
        return redirect('administrateur:gerer_utilisateurs')

class ModifierUtilisateurView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'administrateur':
            return redirect('users:dashboard_etudiant')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, user_id):
        user = get_object_or_404(Utilisateur, id=user_id)
        return render(request, 'administrateur/modifier_utilisateur.html', {'utilisateur': user})
    
    def post(self, request, user_id):
        user = get_object_or_404(Utilisateur, id=user_id)
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.role = request.POST.get('role')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.is_active = request.POST.get('is_active') == 'on'
        if request.POST.get('ine'):
            user.ine = request.POST.get('ine')
        user.save()
        
        messages.success(request, f"Utilisateur {user.username} modifié")
        return redirect('administrateur:gerer_utilisateurs')

class DesactiverUtilisateurView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'administrateur':
            return redirect('users:dashboard_etudiant')
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, user_id):
        user = get_object_or_404(Utilisateur, id=user_id)
        user.is_active = not user.is_active
        user.save()
        status = "activé" if user.is_active else "désactivé"
        messages.success(request, f"Compte {user.username} {status}")
        return redirect('administrateur:gerer_utilisateurs')

# ==================== RAPPORTS ET STATISTIQUES ====================
class StatistiquesView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'administrateur':
            messages.error(request, "Accès réservé aux administrateurs.")
            return redirect('users:dashboard_etudiant')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        from django.db import models
        periode = request.GET.get('periode', 'mois')
        
        if periode == 'semaine':
            date_debut = timezone.now() - timedelta(days=7)
        elif periode == 'mois':
            date_debut = timezone.now() - timedelta(days=30)
        elif periode == 'semestre':
            date_debut = timezone.now() - timedelta(days=180)
        elif periode == 'annee':
            date_debut = timezone.now() - timedelta(days=365)
        else:
            date_debut = timezone.now() - timedelta(days=30)
        
        emprunts_periode = Emprunt.objects.filter(date_emprunt__gte=date_debut)
        
        top_livres = emprunts_periode.values('ouvrage__titre').annotate(total=models.Count('id')).order_by('-total')[:10]
        
        total_emprunts = emprunts_periode.count()
        retards = emprunts_periode.filter(statut='en_retard').count()
        taux_retard = (retards / total_emprunts * 100) if total_emprunts > 0 else 0
        
        retards_par_etudiant = emprunts_periode.filter(statut='en_retard').values('etudiant__first_name', 'etudiant__last_name', 'etudiant__ine').annotate(total=models.Count('id')).order_by('-total')
        
        context = {
            'top_livres': top_livres,
            'taux_retard': round(taux_retard, 2),
            'retards_par_etudiant': retards_par_etudiant,
            'periode': periode,
        }
        return render(request, 'administrateur/statistiques.html', context)

class ExporterRapportView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'administrateur':
            return redirect('users:dashboard_etudiant')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, format_type):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="rapport_{timezone.now().date()}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Étudiant', 'INE', 'Livre', 'Date emprunt', 'Date retour prévue', 'Statut'])
        
        for emprunt in Emprunt.objects.all():
            writer.writerow([
                emprunt.id,
                emprunt.etudiant.get_full_name(),
                emprunt.etudiant.ine or '-',
                emprunt.ouvrage.titre,
                emprunt.date_emprunt.date(),
                emprunt.date_retour_prevue.date(),
                emprunt.statut
            ])
        
        return response

# ==================== GESTION DES LOGS ====================
class ConsulterLogsView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'administrateur':
            messages.error(request, "Accès réservé aux administrateurs.")
            return redirect('users:dashboard_etudiant')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        from apps.statistics.models import LogActivite
        logs = LogActivite.objects.all()
        
        utilisateur_id = request.GET.get('utilisateur')
        action = request.GET.get('action')
        date_debut = request.GET.get('date_debut')
        date_fin = request.GET.get('date_fin')
        
        if utilisateur_id:
            logs = logs.filter(utilisateur_id=utilisateur_id)
        if action:
            logs = logs.filter(action=action)
        if date_debut:
            logs = logs.filter(date_action__date__gte=date_debut)
        if date_fin:
            logs = logs.filter(date_action__date__lte=date_fin)
        
        utilisateurs = Utilisateur.objects.all()
        
        context = {
            'logs': logs,
            'utilisateurs': utilisateurs,
            'filtre_utilisateur': utilisateur_id,
            'filtre_action': action,
            'filtre_date_debut': date_debut,
            'filtre_date_fin': date_fin,
            'actions': LogActivite.ACTION_CHOICES,
        }
        return render(request, 'administrateur/logs.html', context)

# ==================== CONFIGURATION DU SYSTÈME ====================
from apps.statistics.models import ConfigurationSysteme

class ConfigurerSystemeView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'administrateur':
            messages.error(request, "Accès réservé aux administrateurs.")
            return redirect('users:dashboard_etudiant')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        config = ConfigurationSysteme.get_config()
        return render(request, 'administrateur/configurer_systeme.html', {'config': config})
    
    def post(self, request):
        config = ConfigurationSysteme.get_config()
        
        duree = request.POST.get('duree_emprunt_jours')
        tarif = request.POST.get('tarif_penalite_journalier')
        
        if duree:
            config.duree_emprunt_jours = int(duree)
        if tarif:
            config.tarif_penalite_journalier = int(tarif)
        
        config.modifie_par = request.user
        config.save()
        
        from apps.loans.signals import update_config
        update_config(config.duree_emprunt_jours, config.tarif_penalite_journalier)
        
        messages.success(request, "Configuration mise à jour avec succès !")
        return redirect('administrateur:configurer_systeme')

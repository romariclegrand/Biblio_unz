from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from apps.books.models import Ouvrage
from .models import Utilisateur

def accueil(request):
    return render(request, 'users/accueil.html')

class ConnexionView(View):
    def get(self, request):
        return render(request, 'users/login.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            messages.success(request, f'Bienvenue {user.username} !')
            
            if user.role == 'administrateur':
                return redirect('administrateur:dashboard')
            elif user.role == 'bibliothecaire':
                return redirect('bibliothecaire:dashboard')
            else:
                return redirect('users:dashboard_etudiant')
        else:
            messages.error(request, 'Identifiants incorrects.')
            return render(request, 'users/login.html')

class DeconnexionView(View):
    def get(self, request):
        logout(request)
        messages.info(request, 'Déconnecté.')
        return redirect('users:login')

class InscriptionView(View):
    def get(self, request):
        return render(request, 'users/register.html')
    
    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        ine = request.POST.get('ine')
        
        if password != password2:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
            return render(request, 'users/register.html')
        
        if Utilisateur.objects.filter(username=username).exists():
            messages.error(request, 'Nom d\'utilisateur déjà pris.')
            return render(request, 'users/register.html')
        
        if Utilisateur.objects.filter(ine=ine).exists():
            messages.error(request, 'Cet INE est déjà associé à un compte.')
            return render(request, 'users/register.html')
        
        if len(ine) != 12:
            messages.error(request, "L'INE doit contenir exactement 12 caractères.")
            return render(request, 'users/register.html')
        
        user = Utilisateur.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=nom,
            last_name=prenom,
            ine=ine,
            role='etudiant'
        )
        
        login(request, user)
        messages.success(request, 'Inscription réussie !')
        return redirect('users:dashboard_etudiant')

class DashboardEtudiantView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != 'etudiant':
            if request.user.role == 'bibliothecaire':
                return redirect('bibliothecaire:dashboard')
            elif request.user.role == 'administrateur':
                return redirect('administrateur:dashboard')
        
        # Récupérer les 8 derniers livres ajoutés
        derniers_livres = Ouvrage.objects.all().order_by('-date_ajout')[:8]
        
        return render(request, 'users/dashboard_etudiant.html', {
            'user': request.user,
            'derniers_livres': derniers_livres
        })

class ProfilView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'users/profil.html', {'user': request.user})

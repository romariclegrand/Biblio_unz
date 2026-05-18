from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
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
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenue {user.username} !')
            return redirect('users:dashboard')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
            return render(request, 'users/login.html')

class DeconnexionView(View):
    def get(self, request):
        logout(request)
        messages.info(request, 'Vous avez été déconnecté.')
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
        
        if password != password2:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
            return render(request, 'users/register.html')
        
        if Utilisateur.objects.filter(username=username).exists():
            messages.error(request, 'Ce nom d\'utilisateur existe déjà.')
            return render(request, 'users/register.html')
        
        user = Utilisateur.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=nom,
            last_name=prenom,
            role='etudiant'
        )
        
        login(request, user)
        messages.success(request, 'Inscription réussie !')
        return redirect('users:dashboard')

class ProfilView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'users/profil.html', {'user': request.user})

class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        context = {'user': request.user}
        
        if request.user.role == 'etudiant':
            return render(request, 'users/dashboard_etudiant.html', context)
        elif request.user.role == 'bibliothecaire':
            return render(request, 'users/dashboard_bibliothecaire.html', context)
        elif request.user.role == 'administrateur':
            return render(request, 'users/dashboard_administrateur.html', context)
        
        return render(request, 'users/dashboard.html', context)

from django.shortcuts import render, get_object_or_404
from django.views import View
from django.db.models import Q
from .models import Ouvrage, Categorie

class CatalogueView(View):
    """Affiche tous les livres avec recherche et filtrage"""
    def get(self, request):
        livres = Ouvrage.objects.all()
        categories = Categorie.objects.all()
        
        # Récupérer les paramètres de filtrage
        recherche = request.GET.get('recherche', '')
        categorie_id = request.GET.get('categorie', '')
        
        # Appliquer le filtre par recherche
        if recherche:
            livres = livres.filter(
                Q(titre__icontains=recherche) |
                Q(auteur__icontains=recherche) |
                Q(isbn__icontains=recherche)
            )
        
        # Appliquer le filtre par catégorie
        if categorie_id and categorie_id.isdigit():
            livres = livres.filter(categorie_id=int(categorie_id))
        
        context = {
            'livres': livres,
            'categories': categories,
            'recherche': recherche,
            'categorie_selectionnee': categorie_id,
        }
        return render(request, 'books/catalogue.html', context)

class LivreDetailView(View):
    """Affiche les détails d'un livre spécifique"""
    def get(self, request, livre_id):
        livre = get_object_or_404(Ouvrage, id=livre_id)
        context = {
            'livre': livre,
        }
        return render(request, 'books/livre_detail.html', context)

class LivresParCategorieView(View):
    """Affiche les livres d'une catégorie spécifique"""
    def get(self, request, categorie_id):
        categorie = get_object_or_404(Categorie, id=categorie_id)
        livres = Ouvrage.objects.filter(categorie=categorie)
        categories = Categorie.objects.all()
        
        context = {
            'livres': livres,
            'categorie': categorie,
            'categories': categories,
        }
        return render(request, 'books/catalogue.html', context)

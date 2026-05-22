from django.contrib import admin
from .models import Categorie, Ouvrage, HistoriqueOuvrage

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'rayon')
    search_fields = ('nom',)

@admin.register(Ouvrage)
class OuvrageAdmin(admin.ModelAdmin):
    list_display = ('id', 'titre', 'auteur', 'isbn', 'categorie', 'nombre_exemplaires', 'nombre_disponibles', 'rayon')
    list_filter = ('categorie',)
    search_fields = ('titre', 'auteur', 'isbn')
    readonly_fields = ('date_ajout', 'date_modification')

@admin.register(HistoriqueOuvrage)
class HistoriqueOuvrageAdmin(admin.ModelAdmin):
    list_display = ('id', 'ouvrage', 'utilisateur', 'action', 'date_action')
    list_filter = ('action', 'date_action')
    readonly_fields = ('ouvrage', 'utilisateur', 'action', 'details', 'date_action')

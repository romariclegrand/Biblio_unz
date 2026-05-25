from django.contrib import admin
from .models import Categorie, Ouvrage, HistoriqueOuvrage

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'rayon')
    search_fields = ('nom',)

@admin.register(Ouvrage)
class OuvrageAdmin(admin.ModelAdmin):
    list_display = ('id', 'titre', 'auteur', 'isbn', 'categorie', 'maison_edition', 'annee_edition', 'nombre_exemplaires', 'nombre_disponibles')
    list_filter = ('categorie',)
    search_fields = ('titre', 'auteur', 'isbn', 'maison_edition')
    readonly_fields = ('date_ajout', 'date_modification')
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('titre', 'auteur', 'isbn', 'categorie')
        }),
        ('Édition', {
            'fields': ('maison_edition', 'annee_edition')
        }),
        ('Gestion des exemplaires', {
            'fields': ('nombre_exemplaires', 'nombre_disponibles', 'rayon')
        }),
        ('Dates', {
            'fields': ('date_ajout', 'date_modification')
        }),
    )

@admin.register(HistoriqueOuvrage)
class HistoriqueOuvrageAdmin(admin.ModelAdmin):
    list_display = ('id', 'ouvrage', 'utilisateur', 'action', 'date_action')
    list_filter = ('action', 'date_action')
    readonly_fields = ('ouvrage', 'utilisateur', 'action', 'details', 'date_action')

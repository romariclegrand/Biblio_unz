from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from .models import Categorie, Ouvrage

Utilisateur = get_user_model()

# Personnalisation de l'admin utilisateur pour cacher certains champs aux bibliothécaires
class UtilisateurBibliothecaireAdmin(UserAdmin):
    fieldsets = (
        ('Informations personnelles', {'fields': ('username', 'first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'groups')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')

# Désenregistrer l'admin utilisateur par défaut pour le remplacer
try:
    admin.site.unregister(Utilisateur)
except:
    pass
admin.site.register(Utilisateur, UtilisateurBibliothecaireAdmin)

# Admin des catégories
@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description')
    search_fields = ('nom',)

# Admin des ouvrages (CRUD complet)
@admin.register(Ouvrage)
class OuvrageAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'isbn', 'categorie', 'nombre_exemplaires', 'nombre_disponibles', 'statut_affichage')
    list_filter = ('categorie', 'annee_publication')
    search_fields = ('titre', 'auteur', 'isbn')
    fieldsets = (
        ('Informations principales', {
            'fields': ('titre', 'auteur', 'isbn', 'categorie')
        }),
        ('Détails publication', {
            'fields': ('editeur', 'annee_publication')
        }),
        ('Gestion des exemplaires', {
            'fields': ('nombre_exemplaires', 'nombre_disponibles')
        }),
    )
    
    def statut_affichage(self, obj):
        if obj.nombre_disponibles > 0:
            return format_html('<span style="color: green;">✓ Disponible ({})</span>', obj.nombre_disponibles)
        else:
            return format_html('<span style="color: red;">✗ Indisponible</span>')
    statut_affichage.short_description = 'Statut'
    
    # Validation : ISBN unique (déjà géré par le modèle)
    # Validation : suppression impossible si emprunté (on verra plus tard avec loans)
    
    def delete_view(self, request, object_id, extra_context=None):
        from django.contrib import messages
        from django.shortcuts import redirect
        from django.urls import reverse
        
        obj = self.get_object(request, object_id)
        
        # Vérifier si le livre est emprunté (à compléter quand on aura le modèle Emprunt)
        # Pour l'instant, on autorise la suppression
        return super().delete_view(request, object_id, extra_context)
    
    def save_model(self, request, obj, form, change):
        if obj.nombre_disponibles > obj.nombre_exemplaires:
            obj.nombre_disponibles = obj.nombre_exemplaires
        super().save_model(request, obj, form, change)

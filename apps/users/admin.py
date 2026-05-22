from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur

class UtilisateurAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'ine', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'ine')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informations complémentaires', {
            'fields': ('role', 'telephone', 'ine', 'actif')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations complémentaires', {
            'fields': ('role', 'telephone', 'ine')
        }),
    )

admin.site.register(Utilisateur, UtilisateurAdmin)

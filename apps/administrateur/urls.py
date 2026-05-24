from django.urls import path
from . import views

app_name = 'administrateur'

urlpatterns = [
    path('dashboard/', views.DashboardAdminView.as_view(), name='dashboard'),
    path('utilisateurs/', views.GererUtilisateursView.as_view(), name='gerer_utilisateurs'),
    path('utilisateurs/ajouter/', views.AjouterUtilisateurView.as_view(), name='ajouter_utilisateur'),
    path('utilisateurs/modifier/<int:user_id>/', views.ModifierUtilisateurView.as_view(), name='modifier_utilisateur'),
    path('utilisateurs/desactiver/<int:user_id>/', views.DesactiverUtilisateurView.as_view(), name='desactiver_utilisateur'),
    path('statistiques/', views.StatistiquesView.as_view(), name='statistiques'),
    path('exporter/<str:format_type>/', views.ExporterRapportView.as_view(), name='exporter'),
    path('logs/', views.ConsulterLogsView.as_view(), name='logs'),
    path('configurer/', views.ConfigurerSystemeView.as_view(), name='configurer_systeme'),
]

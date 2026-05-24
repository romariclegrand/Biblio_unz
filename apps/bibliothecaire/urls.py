from django.urls import path
from . import views

app_name = 'bibliothecaire'

urlpatterns = [
    path('dashboard/', views.DashboardBibliothecaireView.as_view(), name='dashboard'),
    path('catalogue/', views.GererCatalogueView.as_view(), name='gerer_catalogue'),
    path('catalogue/ajouter/', views.AjouterLivreView.as_view(), name='ajouter_livre'),
    path('catalogue/modifier/<int:livre_id>/', views.ModifierLivreView.as_view(), name='modifier_livre'),
    path('catalogue/supprimer/<int:livre_id>/', views.SupprimerLivreView.as_view(), name='supprimer_livre'),
    path('emprunts/', views.GererEmpruntsView.as_view(), name='gerer_emprunts'),
    path('emprunts/retour/<int:emprunt_id>/', views.EnregistrerRetourView.as_view(), name='enregistrer_retour'),
    path('emprunts/rappel/<int:emprunt_id>/', views.EnvoyerRappelView.as_view(), name='envoyer_rappel'),
    path('penalites/', views.GererPenalitesView.as_view(), name='gerer_penalites'),
    path('penalites/annuler/<int:penalite_id>/', views.AnnulerPenaliteView.as_view(), name='annuler_penalite'),
    path('penalites/payer/<int:penalite_id>/', views.MarquerPenalitePayeeView.as_view(), name='payer_penalite'),
    path('penalites/exporter/<str:format_type>/', views.ExporterPenalitesView.as_view(), name='exporter_penalites'),
    path('reservations/', views.GererReservationsView.as_view(), name='gerer_reservations'),
]

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('login/', views.ConnexionView.as_view(), name='login'),
    path('logout/', views.DeconnexionView.as_view(), name='logout'),
    path('register/', views.InscriptionView.as_view(), name='register'),
    path('profil/', views.ProfilView.as_view(), name='profil'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]

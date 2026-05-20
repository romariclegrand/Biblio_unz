from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.CatalogueView.as_view(), name='catalogue'),
    path('livre/<int:livre_id>/', views.LivreDetailView.as_view(), name='livre_detail'),
    path('categorie/<int:categorie_id>/', views.LivresParCategorieView.as_view(), name='livres_par_categorie'),
]

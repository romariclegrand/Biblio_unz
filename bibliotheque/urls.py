from django.contrib import admin
from django.urls import path, include
from apps.users.views import accueil

urlpatterns = [
    path('', accueil, name='accueil'),
    path('admin/', admin.site.urls),
    path('users/', include('apps.users.urls')),
    path('books/', include('apps.books.urls')),
    path('loans/', include('apps.loans.urls')),
    path('bibliothecaire/', include('apps.bibliothecaire.urls')),
    path('administrateur/', include('apps.administrateur.urls')),
]

from django.contrib import admin
from django.urls import path, include
from apps.users.views import accueil
from apps.users.create_accounts import create_accounts
from apps.users.create_accounts import create_accounts
from apps.users.migrate_db import run_migrations

urlpatterns = [
    path('', accueil, name='accueil'),
    path('create-accounts/', create_accounts, name='create_accounts'),
    path('create-accounts/', create_accounts, name='create_accounts'),
    path('migrate/', run_migrations, name='migrate'),
    path('admin/', admin.site.urls),
    path('users/', include('apps.users.urls')),
    path('books/', include('apps.books.urls')),
    path('loans/', include('apps.loans.urls')),
    path('bibliothecaire/', include('apps.bibliothecaire.urls')),
    path('administrateur/', include('apps.administrateur.urls')),
    path('apropos/', include('apps.core.urls')),
]

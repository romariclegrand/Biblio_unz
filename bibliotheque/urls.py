from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.users.views import accueil

urlpatterns = [
    path('', accueil, name='accueil'),
    path('admin/', admin.site.urls),
    path('users/', include('apps.users.urls')),
    path('books/', include('apps.books.urls')),
    path('loans/', include('apps.loans.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('statistics/', include('apps.statistics.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

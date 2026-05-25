from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.AProposView.as_view(), name='apropos'),
]

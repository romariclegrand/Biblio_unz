from django.urls import path
from . import views

app_name = 'loans'

urlpatterns = [
    path('emprunter/<int:livre_id>/', views.EmprunterView.as_view(), name='emprunter'),
    path('mes-emprunts/', views.MesEmpruntsView.as_view(), name='mes_emprunts'),
]

from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('medications/', views.medication_list, name='medication_list'),
    path('medications/new/', views.medication_create, name='medication_create'),
    path('medications/<int:pk>/delete/', views.medication_delete, name='medication_delete'),
    path('medications/<int:pk>/toggle/', views.medication_toggle, name='medication_toggle'),
    path('records/', views.records_list, name='records'),
    path('health/', views.health_profile, name='health_profile'),
]

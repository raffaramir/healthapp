from django.urls import path
from . import views

app_name = 'labs'

urlpatterns = [
    path('', views.lab_list, name='list'),
    path('<int:pk>/', views.lab_detail, name='detail'),
]

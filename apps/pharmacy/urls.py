from django.urls import path
from . import views

app_name = 'pharmacy'

urlpatterns = [
    path('', views.pharmacy_list, name='list'),
    path('<int:pk>/', views.pharmacy_detail, name='detail'),
]

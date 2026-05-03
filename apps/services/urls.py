from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.request_list, name='request_list'),
    path('new/', views.request_select, name='request_select'),
    path('new/<str:service_type>/', views.request_create, name='request_create'),
    path('<int:pk>/', views.request_detail, name='request_detail'),
    path('<int:pk>/cancel/', views.request_cancel, name='request_cancel'),
    path('<int:pk>/action/', views.provider_action, name='provider_action'),
    path('<int:pk>/respond/', views.provider_respond, name='provider_respond'),
]

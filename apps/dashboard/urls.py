from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('pending/', views.pending_approval, name='pending_approval'),

    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/<int:user_id>/action/', views.admin_user_action, name='admin_user_action'),
    path('admin/requests/', views.admin_requests, name='admin_requests'),
    path('admin/logs/', views.admin_logs, name='admin_logs'),
]

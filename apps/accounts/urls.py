from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_select, name='register_select'),
    path('register/<str:role>/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('verify/<uuid:token>/', views.verify_email, name='verify_email'),
]

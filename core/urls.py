from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('', home, name='home'),
    path('login/', login_user, name='login'),
    path('register/', register_user, name='register'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', logout_user, name='logout'),
    path('add-service/', add_service, name='add_service'),
    path('order/<int:service_id>/', create_order, name='create_order'),
    path('chat/', views.chat_view, name='chat'),
]
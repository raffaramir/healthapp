from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.conversation_list, name='conversation_list'),
    path('directory/', views.chat_directory, name='directory'),
    path('start/<int:user_id>/', views.start_conversation, name='start'),
    path('<int:pk>/', views.conversation_view, name='conversation'),
]

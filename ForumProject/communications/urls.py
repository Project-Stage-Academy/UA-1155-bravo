from django.urls import path
from .views import CreateConversationView, SendMessageView, ListMessagesView
from . import views

app_name = 'communications'

urlpatterns = [
    path('', views.index_view, name='chat-index'),
    path('<int:user_id>/', views.room_view, name='chat-room'),
    path('api/conversations/', views.create_conversation, name='create-conversation'),
    path('api/messages/', views.send_message, name='send-message'),
    path('api/conversations/<int:conversation_id>/messages/', views.ListMessagesView.as_view(), name='list-messages'),
]
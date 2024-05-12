from django.urls import path
from .views import CreateConversationView, SendMessageView, ListMessagesView
from . import views

app_name = 'communications'

urlpatterns = [
    path('', views.index_view, name='chat-index'),
    path('<int:user_id>/', views.room_view, name='chat-room'),
    path('conversations/', CreateConversationView.as_view(), name='create-conversation'),
    path('messages/', SendMessageView.as_view(), name='send-message'),
    path('conversations/<int:conversation_id>/messages/', ListMessagesView.as_view(), name='list-messages'),
]
from django.urls import path
from .views import CreateConversationView, SendMessageView, ListMessagesView, load_messages
from . import views

app_name = 'communications'

urlpatterns = [
    path('', views.index_view, name='chat-index'),
    path('<int:user_id>/', views.room_view, name='chat-room'),
    path('conversations/', CreateConversationView.as_view(), name='create-conversation'),
    path('messages/', SendMessageView.as_view(), name='send-message'),
    path('conversations/<int:conversation_id>/messages/', ListMessagesView.as_view(), name='list-messages'),
    path('api/load-messages/<int:room_id>/', load_messages, name='load_messages'),
]
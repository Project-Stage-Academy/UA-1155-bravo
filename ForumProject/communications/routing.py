from django.urls import path
from .consumers import ChatNotificationConsumer
from . import consumers

websocket_urlpatterns = [
    path('ws/chat/<str:room_name>/', consumers.ChatConsumer.as_asgi()),
    path('ws/chat_notifications/', ChatNotificationConsumer.as_asgi()),
]

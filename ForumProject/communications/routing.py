from django.urls import path
from .consumers import ChatConsumer, ChatNotificationConsumer

websocket_urlpatterns = [
    path('ws/chat/<str:room_name>/', ChatConsumer.as_asgi()),
    path('ws/chat_notifications/', ChatNotificationConsumer.as_asgi()),
]

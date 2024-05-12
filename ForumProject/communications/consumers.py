import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Room, Message


class ChatConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_name = None
        self.room_group_name = None
        self.room = None
        self.messages = None
        self.user = None
        self.user_inbox = None

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.room = Room.objects.get(name=self.room_name)
        self.messages = Message.objects.filter(room=self.room)
        self.user = self.scope['user']
        self.user_inbox = f'inbox_{self.user.first_name}'

        self.accept()

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name,
        )

        self.send(json.dumps({
            'type': 'user_list',
            'users': [user.first_name for user in self.room.online.all()],
        }))

        if self.user.is_authenticated:
            async_to_sync(self.channel_layer.group_add)(
                self.user_inbox,
                self.channel_name,
            )
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'users_messages',
                    'messages': [str(message) for message in self.messages],
                }
            )
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'user_join',
                    'user': self.user.first_name,
                }
            )

            self.room.online.add(self.user)

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name,
        )

        if self.user.is_authenticated:
            async_to_sync(self.channel_layer.group_discard)(
                self.user_inbox,
                self.channel_name,
            )

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'user_leave',
                    'user': self.user.first_name,
                }
            )
            self.room.online.remove(self.user)

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        if not self.user.is_authenticated:
            return

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'user': self.user.first_name,
                'message': message,
            }
        )
        Message.objects.create(user=self.user, room=self.room, content=message)

    def chat_message(self, event):
        self.send(text_data=json.dumps(event))

    def user_join(self, event):
        self.send(text_data=json.dumps(event))

    def users_messages(self, event):
        self.send(text_data=json.dumps(event))

    def user_leave(self, event):
        self.send(text_data=json.dumps(event))

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = f'notifications_{self.scope["user"].id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from room group
    async def send_notification(self, event):
        notification = event['notification']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'notification': notification
        }))


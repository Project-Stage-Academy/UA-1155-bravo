import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

from .utils import get_room, get_messages, get_online_users, get_user_first_name, \
    add_user_to_online, remove_user_from_online, create_message

logger = logging.getLogger('django.server')


class ChatConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_name = None
        self.room_group_name = None
        self.room = None
        self.messages = None
        self.user = None
        self.user_inbox = None

    async def connect(self):
        if not self.scope['user'].is_authenticated:
            logger.info(f'the user is not authenticated')
            await self.close()
            return

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.room = await get_room(self.room_name)
        self.messages = await get_messages(self.room)
        self.user = self.scope['user']
        self.user_inbox = f'inbox_{self.user.first_name}'

        await self.accept()

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.send(json.dumps({
            'type': 'user_list',
            'users': await get_online_users(self.room),
        }))

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_join',
                'user': await get_user_first_name(self.user),
            }
        )
        logger.info(f'{self.user.email} has connected to the room')
        await add_user_to_online(self.room, self.user)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

        if self.user.is_authenticated:
            await self.channel_layer.group_discard(
                self.user_inbox,
                self.channel_name,
            )

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_leave',
                    'user': await get_user_first_name(self.user),
                }
            )
            logger.info(f'{self.user.email} has disconnected from the room')
            await remove_user_from_online(self.room, self.user)

    async def receive(self, text_data=None, bytes_data=None):
        try:
            text_data_json = json.loads(text_data)
        except json.JSONDecodeError:
            logging.error("Error: Failed to parse JSON data.")
            return
        message = text_data_json['message']

        if not self.user.is_authenticated:
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'user': await get_user_first_name(self.user),
                'message': message,
            }
        )

        logger.info(f'Message sent by {self.user.email}')
        await create_message(self.user, self.room, message)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def user_join(self, event):
        await self.send(text_data=json.dumps(event))

    async def users_messages(self, event):
        await self.send(text_data=json.dumps(event))

    async def user_leave(self, event):
        await self.send(text_data=json.dumps(event))


class ChatNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope['user'].is_authenticated:
            await self.close()
            return

        self.room_group_name = f'chat_notifications_{self.scope["user"].id}'

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
    async def send_chat_notification(self, event):
        chat_notification = event['chat_notification']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'chat_notification': chat_notification
        }))


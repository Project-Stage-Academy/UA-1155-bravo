import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from .models import Message, ChatNotification, Room
from django.dispatch import receiver
from django.db.models.signals import post_save
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

User = get_user_model()

@receiver(post_save, sender=Message)
def create_chat_notification(sender, instance, created, **kwargs):
    if created:
        room = instance.room
        for user in room.online.all():
            ChatNotification.objects.create(
                recipient=user,
                message=instance
            )
            logger.debug(f'ChatNotification created for user {user.username} and message {instance.content}')

@receiver(post_save, sender=Message)
def send_chat_notification_via_channels(sender, instance, created, **kwargs):
    if created:
        room = instance.room
        channel_layer = get_channel_layer()
        for user in room.online.all():
            async_to_sync(channel_layer.group_send)(
                f'chat_notifications_{user.id}',
                {
                    'type': 'send_chat_notification',
                    'chat_notification': f'New message in {room.name}'
                }
            )
            logger.debug(f'Notification sent via channel layer for user {user.username}')

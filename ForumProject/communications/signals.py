from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from .models import Message, Notification
from django.dispatch import receiver
from django.db.models.signals import post_save
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance.user,
            message=instance
        )

@receiver(post_save, sender=Message)
def send_notification_via_channels(sender, instance, created, **kwargs):
    if created:
        notification = Notification.objects.create(
            recipient=instance.room.online,
            message=instance
        )
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'notifications_{instance.room.online.id}',
            {
                'type': 'send_notification',
                'notification': f'New message in {instance.room.name}'
            }
        )
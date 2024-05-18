import logging

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async

from communications.models import Room, Message


@database_sync_to_async
def get_room(room_name):
    try:
        return Room.objects.get(name=room_name)
    except Room.DoesNotExist:
        logging.error("Error: Failed to return Room.")


@database_sync_to_async
def get_messages(room):
    return Message.objects.filter(room=room)


@database_sync_to_async
def create_message(user, room, message):
    return Message.objects.create(user=user, room=room, content=message)


@sync_to_async
def get_online_users(room):
    return [user.first_name for user in room.online.all()]


@database_sync_to_async
def add_user_to_online(room, user):
    return room.online.add(user)


@database_sync_to_async
def remove_user_from_online(room, user):
    return room.online.remove(user)


@sync_to_async
def get_user_first_name(user):
    return user.first_name

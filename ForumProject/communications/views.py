from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.core.signing import BadSignature
from .models import Room, Message
from django_ratelimit.decorators import ratelimit
import logging
from django.http import JsonResponse




User = get_user_model()

logger = logging.getLogger(__name__)

@login_required
@ratelimit(key='user', rate='5/m', block=True)
def index_view(request):
    users = User.objects.exclude(id=request.user.id)
    rooms_list = Room.objects.filter(name__contains=str(request.user.id))
    
    logger.info(f"User  with email {request.user.email} accessed the index page")
   
    return render(request, 'index.html', {
        'rooms': rooms_list, 'users': users
    })


@login_required
@ratelimit(key='user', rate='5/m', block=True)
def room_view(request, user_id):
    try:
        user = get_object_or_404(User, id=user_id)
        if request.user.id > user.id:
            thread_name = f'chat_{request.user.id}_{user.id}'
        else:
            thread_name = f'chat_{user.id}_{request.user.id}'
        chat_room, created = Room.objects.get_or_create(name=thread_name)

        messages = Message.objects.filter(room=chat_room)
        users_messages = '\n'.join([str(message) for message in messages])+'\n'
    except BadSignature:
        users_messages = 'Error: Invalid message decryption key'

    logger.info(f"User with email {request.user.email} viewed the chat room with user ID {user_id}")

    return render(request, 'room.html', {
        'room': chat_room, 'users_messages': users_messages
    })
    
    
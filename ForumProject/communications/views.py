from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404

from users.models import UserRoleCompany, UserStartup
from django.core.signing import BadSignature
from .models import Room, Message
from django_ratelimit.decorators import ratelimit
import logging
from django.http import JsonResponse


User = get_user_model()

logger = logging.getLogger('django.server')


@login_required
@ratelimit(key='user', rate='5/m', block=True)
def index_view(request):
    user_role = UserRoleCompany.objects.filter(user=request.user).exists()
    if not user_role:
        raise PermissionDenied
    users = []
    if request.user.user_info.role == 'investor':
        startups = UserStartup.objects.all().values_list('customuser', flat=True)
        users = User.objects.filter(id__in=startups).exclude(id=request.user.id)
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
        user_role = UserRoleCompany.objects.filter(user=request.user).exists()

        if request.user.id > user.id:
            thread_name = f'chat_{request.user.id}_{user.id}'
        else:
            thread_name = f'chat_{user.id}_{request.user.id}'

        if not user_role or (request.user.user_info.role != 'investor'
                             and not Room.objects.filter(name=thread_name).exists()):
            raise PermissionDenied
        chat_room, created = Room.objects.get_or_create(name=thread_name)

        messages = Message.objects.filter(room=chat_room)
        users_messages = '\n'.join([str(message) for message in messages])+'\n'
    except BadSignature:
        users_messages = 'Error: Invalid message decryption key'

    logger.info(f"User with email {request.user.email} viewed the chat room with user ID {user_id}")

    return render(request, 'room.html', {
        'room': chat_room, 'users_messages': users_messages
    })
    
    
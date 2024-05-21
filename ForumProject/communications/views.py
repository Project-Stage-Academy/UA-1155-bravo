from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404

from users.models import UserRoleCompany
from .models import Room, Message

User = get_user_model()


@login_required
def index_view(request):
    user_role = UserRoleCompany.objects.filter(user=request.user).exists()
    if not user_role:
        raise PermissionDenied
    users = []
    if request.user.user_info.role == 'investor':
        users = User.objects.exclude(id=request.user.id)
    rooms_list = Room.objects.filter(name__contains=str(request.user.id))
    return render(request, 'index.html', {
        'rooms': rooms_list, 'users': users
    })


@login_required
def room_view(request, user_id):
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
    return render(request, 'room.html', {
        'room': chat_room, 'users_messages': users_messages
    })

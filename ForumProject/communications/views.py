from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404

from .models import Room

User = get_user_model()


def index_view(request):
    users = User.objects.all()
    return render(request, 'index.html', {
        'rooms': Room.objects.all(), 'users': users
    })


def room_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.user.id > user.id:
        thread_name = f'chat_{request.user.id}-{user.id}'
    else:
        thread_name = f'chat_{user.id}-{request.user.id}'
    chat_room, created = Room.objects.get_or_create(name=thread_name)
    return render(request, 'room.html', {
        'room': chat_room,
    })

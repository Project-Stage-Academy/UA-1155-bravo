from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from .models import Room

User = get_user_model()


@login_required
def index_view(request):
    users = User.objects.exclude(id=request.user.id)
    rooms_list = Room.objects.filter(name__contains=str(request.user.id))
    return render(request, 'index.html', {
        'rooms': rooms_list, 'users': users
    })


@login_required
def room_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.user.id > user.id:
        thread_name = f'chat_{request.user.id}_{user.id}'
    else:
        thread_name = f'chat_{user.id}_{request.user.id}'
    chat_room, created = Room.objects.get_or_create(name=thread_name)
    return render(request, 'room.html', {
        'room': chat_room,
    })

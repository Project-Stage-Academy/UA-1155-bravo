from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .serializers import RoomSerializer, MessageSerializer
from .models import Room, Message

from .models import Room, Message
from rest_framework import generics

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

    messages = Message.objects.filter(room=chat_room)
    users_messages = '\n'.join([str(message) for message in messages])+'\n'
    return render(request, 'room.html', {
        'room': chat_room, 'users_messages': users_messages
    })

class CreateConversationView(generics.CreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class SendMessageView(generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

class ListMessagesView(generics.ListAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        conversation_id = self.kwargs['conversation_id']
        return Message.objects.filter(room__id=conversation_id)
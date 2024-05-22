from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from .models import Room, Message

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import CreateConversationSerializer, RoomSerializer, MessageSerializer, ListMessagesSerializer

from rest_framework.generics import ListAPIView


@api_view(['POST'])
def create_conversation(request):
    serializer = CreateConversationSerializer(data=request.data)
    if serializer.is_valid():
        participants = serializer.validated_data['participants']
        participant_names = "_".join(map(str, sorted(participants)))
        room_name = f"chat_{participant_names}"
        room, created = Room.objects.get_or_create(name=room_name)
        if created:
            room.online.set(User.objects.filter(id__in=participants))
            room.save()
        room_serializer = RoomSerializer(room)
        return Response(room_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from .serializers import SendMessageSerializer

@api_view(['POST'])
def send_message(request):
    serializer = SendMessageSerializer(data=request.data)
    if serializer.is_valid():
        conversation_id = serializer.validated_data['conversation_id']
        text = serializer.validated_data['text']
        room = get_object_or_404(Room, id=conversation_id)
        user = request.user
        message = Message.objects.create(room=room, user=user, content=text)
        message_serializer = MessageSerializer(message)
        return Response(message_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ListMessagesView(ListAPIView):
    serializer_class = ListMessagesSerializer

    def get_queryset(self):
        conversation_id = self.kwargs['conversation_id']
        return Message.objects.filter(room__id=conversation_id)

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
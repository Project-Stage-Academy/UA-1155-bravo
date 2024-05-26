from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404

from .serializers import RoomSerializer, MessageSerializer
from .models import Room, Message
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from users.models import UserRoleCompany, UserStartup
from django.core.signing import BadSignature
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


@api_view(['GET'])
@login_required
def load_messages(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    messages = Message.objects.filter(room=room).order_by('-timestamp')
    paginator = Paginator(messages, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    serialized_messages = MessageSerializer(page_obj, many=True)
    return Response({
        'messages': serialized_messages.data,
        'has_next': page_obj.has_next()
    })

def too_many_requests(request, exception): 
    return render(request, 'ratelimit.html', status=429)

class CreateConversationView(generics.CreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class SendMessageView(generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

class ListMessagesView(generics.ListAPIView):
    serializer_class = MessageSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        conversation_id = self.kwargs['conversation_id']
        return Message.objects.filter(room__id=conversation_id)

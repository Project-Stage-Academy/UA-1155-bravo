from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .serializers import RoomSerializer, MessageSerializer
from .models import Room, Message
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from .models import Room, Message

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
        'room': chat_room
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
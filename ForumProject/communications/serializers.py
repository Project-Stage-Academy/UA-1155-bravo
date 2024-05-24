from rest_framework import serializers
from communications.models import Room, Message

class CreateConversationSerializer(serializers.Serializer):
    participants = serializers.ListField(child=serializers.IntegerField())

class SendMessageSerializer(serializers.Serializer):
    conversation_id = serializers.IntegerField()
    text = serializers.CharField(max_length=512)

class ListMessagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'user', 'content', 'timestamp']

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
from rest_framework import serializers
from .models import Message

class CreateConversationSerializer(serializers.Serializer):
    participants = serializers.ListField(child=serializers.IntegerField())

class SendMessageSerializer(serializers.Serializer):
    conversation_id = serializers.IntegerField()
    text = serializers.CharField(max_length=512)

class ListMessagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'user', 'content', 'timestamp']

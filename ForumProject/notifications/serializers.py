from rest_framework import serializers
from .models import NotificationPreference

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = ['new_follows', 'new_messages', 'project_updates']

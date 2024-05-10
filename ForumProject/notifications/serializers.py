from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['project', 'startup', 'investor', 'trigger', 'initiator', 'date_time']
        read_only_fields = ['project', 'startup', 'investor', 'trigger', 'initiator', 'date_time']

from rest_framework import serializers
from .models import Notification, NotificationPreferences


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['project', 'startup', 'investor', 'trigger', 'initiator', 'date_time']
        read_only_fields = ['project', 'startup', 'investor', 'trigger', 'initiator', 'date_time']

class NotificationPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreferences
        fields = ['email_on_followers_change',
            'email_on_share_subscription',
            'in_app_on_followers_change',
            'in_app_on_share_subscription'
            ]

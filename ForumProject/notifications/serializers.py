from rest_framework import serializers
from .models import Notification, NotificationPreferences


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Notification model.

    Serializes Notification instances for API representation.

    Attributes:
        project (str): Project associated with the notification.
        startup (str): Startup associated with the notification.
        investor (str): Investor associated with the notification.
        trigger (str): Trigger of the notification.
        initiator (str): Initiator of the notification.
        date_time (datetime): Date and time when the notification occurred.
    """
    class Meta:
        model = Notification
        fields = ['project', 'startup', 'investor', 'trigger', 'initiator', 'date_time']
        read_only_fields = ['project', 'startup', 'investor', 'trigger', 'initiator', 'date_time']

class NotificationPreferencesSerializer(serializers.ModelSerializer):
    """
    Serializer for the NotificationPreferences model.

    Serializes NotificationPreferences instances for API representation.

    Attributes:
        startup_id (int): ID of the startup associated with the notification preferences.
        email_on_followers_change (bool): Whether to send email notifications on followers change.
        email_on_share_subscription (bool): Whether to send email notifications on share subscription change.
        in_app_on_followers_change (bool): Whether to send in-app notifications on followers change.
        in_app_on_share_subscription (bool): Whether to send in-app notifications on share subscription change.
    """
    startup_id = serializers.SerializerMethodField()

    def get_startup_id(self, obj):
        """
        Retrieve the ID of the associated startup.

        Args:
            obj (NotificationPreferences): The NotificationPreferences instance.

        Returns:
            int: The ID of the associated startup.
        """
        return self.context.get('startup_id')
    class Meta:
        model = NotificationPreferences
        fields = [
            'startup_id',
            'email_on_followers_change',
            'email_on_share_subscription',
            'in_app_on_followers_change',
            'in_app_on_share_subscription'
        ]

from rest_framework import serializers
from .models import Notification, StartupNotificationPrefs, InvestorNotificationPrefs


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

class StartupNotificationPrefsSerializer(serializers.ModelSerializer):
    """
    Serializer for the StartupNotificationPrefs model.

    Serializes StartupNotificationPrefs instances for API representation.

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
            obj (StartupNotificationPrefs): The StartupNotificationPrefs instance.

        Returns:
            int: The ID of the associated startup.
        """
        return self.context.get('startup_id')
    class Meta:
        model = StartupNotificationPrefs
        fields = [
            'startup_id',
            'email_project_followers_change',
            'email_project_subscription_change',
            'push_project_followers_change',
            'push_project_subscription_change',
            'email_startup_subscribed',
            'email_startup_unsubscribed',
            'push_startup_subscribed',
            'push_startup_unsubscribed'
        ]

class InvestorNotificationPrefsSerializer(serializers.ModelSerializer):
    """
    TODO
    """
    investor_id = serializers.SerializerMethodField()

    def get_investor_id(self, obj):
        """
        Retrieve the ID of the associated investor.

        Args:
            obj (InvestorNotificationPrefs): The InvestorNotificationPrefs instance.

        Returns:
            int: The ID of the associated investor.
        """
        return self.context.get('investor_id')
    class Meta:
        model = InvestorNotificationPrefs
        fields = [
            'investor_id',
            'email_project_profile_change',
            'push_project_profile_change',
            'email_startup_profile_update',
            'push_startup_profile_update'
        ]

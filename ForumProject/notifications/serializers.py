"""
Module for serializers related to notifications.

This module contains serializers for the Notification model and its associated models.

Classes:
    NotificationSerializer: Serializer for the Notification model.
    StartupNotificationPrefsSerializer: Serializer for the StartupNotificationPrefs model.
    InvestorNotificationPrefsSerializer: Serializer for the InvestorNotificationPrefs model.
"""

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

    Attributes: startup_id (int): ID of the associated startup.
    email_project_on_investor_interest_change (bool): Email preference for project on investor
    interest change. push_project_on_investor_interest_change (bool): Push notification
    preference for project on investor interest change. email_startup_on_investor_interest_change
    (bool): Email preference for startup on investor interest change.
    push_startup_on_investor_interest_change (bool): Push notification preference for startup on
    investor interest change.
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
            'email_project_on_investor_interest_change',
            'push_project_on_investor_interest_change',
            'email_startup_on_investor_interest_change',
            'push_startup_on_investor_interest_change'
        ]


class InvestorNotificationPrefsSerializer(serializers.ModelSerializer):
    """
    Serializer for the InvestorNotificationPrefs model.

    Serializes InvestorNotificationPrefs instances for API representation.

    Attributes: investor_id (int): ID of the associated investor. email_project_profile_change (
    bool): Email preference for project profile changes. push_project_profile_change (bool): Push
    notification preference for project profile changes. email_startup_profile_update (bool):
    Email preference for startup profile updates. push_startup_profile_update (bool): Push
    notification preference for startup profile updates.
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

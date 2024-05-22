from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from startups.models import Startup
from notifications.models import Notification, StartupNotificationPrefs
from subscriptions.models import SubscribeInvestorStartup


        
@receiver(post_save, sender=Startup)
def send_notification_on_startup_update(sender, instance, created, **kwargs):
    """
    Signal receiver to send notifications when a startup is updated.

    This function is triggered after saving a Startup instance. It checks if the startup is not created
    (i.e., it's being updated), then retrieves all subscribers of the startup and creates a notification
    for each subscriber.

    """
    if not created:
        # Get all subscribers of the startup
        subscribers = SubscribeInvestorStartup.objects.filter(startup=instance)
        # Create notifications for each subscriber
        for subscriber in subscribers:
            Notification.objects.create(
                startup=instance,
                investor=subscriber.investor,
                trigger='Startup profile updated',
                initiator='startup'
            )
    
    else:
        StartupNotificationPrefs.objects.create(startup=instance)
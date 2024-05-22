from django.db.models.signals import post_save
from django.dispatch import receiver
from investors.models import Investor
from .models import InvestorNotificationPrefs


@receiver(post_save, sender=Investor)
def set_notification_preferences_for_investor(sender, instance, created, **kwargs):
    """
    TODO - creates Notifications Preferences with default values for any newly created Investor
    """
    if created:
        InvestorNotificationPrefs.objects.create(investor=instance)
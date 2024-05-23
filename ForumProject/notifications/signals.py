from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .utils import send_email_async
from django.db import DatabaseError
import logging
import threading

from .models import Notification, StartupNotificationPrefs, InvestorNotificationPrefs
from projects.models import Project, InvestorProject
from startups.models import Startup
from subscriptions.models import SubscribeInvestorStartup
from investors.models import Investor
from users.models import UserStartup

logger = logging.getLogger(__name__)

def record_notifications(notifications):
    """
    Helper function. Records a list of notifications in the database.

    Args:
        notifications (list or Notification): A list of Notification objects or a single Notification object.

    Returns:
        list: The list of Notification objects that were successfully created in the database.

    Raises:
        DatabaseError: If there is an issue while creating notifications in the database.
    """
    if not isinstance(notifications, list):
        notifications = [notifications]
    
    try:
        return Notification.objects.bulk_create(notifications)
    except DatabaseError as db_err:
        logger.error(f'Database error while creating notifications: {str(db_err)}')
    

def send_notifications(notifications):
    """
    Helper function. Sends notifications to the relevant recipients via email or push notification.

    Args:
        notifications (list): A list of Notification objects to be sent.

    Side Effects:
        - Starts a new thread to send emails asynchronously.
        - Prints a message to the console for push notifications (placeholder for actual implementation).
    """
    for notification in notifications:
        project_msg = f'Project {notification.project} of ' if notification.project else ''
        subject = f'Update on {project_msg}Startup {notification.startup}'
        message = f'{notification.trigger}. Please check the relevant profile page.'
        if notification.initiator == 'investor':
            recipient = notification.startup
            emails = [user_startup.customuser.email for user_startup in recipient.userstartup_set.all()]
            email_prefs = recipient.startup_notice_prefs.active_email_preferences
            push_prefs = recipient.startup_notice_prefs.active_push_preferences
        else:
            recipient = notification.investor
            emails = [user_investor.customuser.email for user_investor in recipient.userinvestor_set.all()]
            email_prefs = recipient.investor_notice_prefs.active_email_preferences
            push_prefs = recipient.investor_notice_prefs.active_push_preferences
        if notification.trigger in email_prefs:
            email_thread = threading.Thread(target=send_email_async, args=(subject, message, emails))
            email_thread.start()
        if notification.trigger in push_prefs:
            print(message) # This is a placeholder for "in app" / push notifications implementation

@receiver(post_save, sender=Investor)
def set_notification_preferences_for_investor(sender, instance, created, **kwargs):
    """
    Sets default notification preferences for a newly created Investor.

    Args:
        sender (Model): The model class that triggered the signal.
        instance (Investor): The instance of the Investor that was saved.
        created (bool): A boolean indicating whether a new instance was created.
        **kwargs: Additional keyword arguments.
    """
    if created:
        InvestorNotificationPrefs.objects.create(investor=instance)

@receiver(post_save, sender=Startup)
def startup_set_notification_prefs_and_notify_updates(sender, instance, created, **kwargs):
    """
    Sets default notification preferences for a newly created Startup or notifies investors if the Startup profile is updated.

    Args:
        sender (Model): The model class that triggered the signal.
        instance (Startup): The instance of the Startup that was saved.
        created (bool): A boolean indicating whether a new instance was created.
        **kwargs: Additional keyword arguments.
    """
    if created:
        StartupNotificationPrefs.objects.create(startup=instance)
    elif SubscribeInvestorStartup.objects.filter(startup=instance):
        trigger = 'Startup profile updated'
        addressees = Investor.objects.filter(subscribeinvestorstartup__startup=instance)
        for addressee in addressees:
            email_prefs_list = [pref.strip() for pref in addressee.investor_notice_prefs.active_email_preferences.split(',')]
            push_prefs_list = [pref.strip() for pref in addressee.investor_notice_prefs.active_push_preferences.split(',')]
            if trigger in email_prefs_list or trigger in push_prefs_list:
                notifications = []
                notification = Notification(
                    startup = instance,
                    investor = addressee,
                    trigger = trigger,
                    initiator = 'startup'
                )
                notifications.append(notification)
        if notifications:
            record_notifications(notifications)
            send_notifications(notifications)

@receiver(post_save, sender=Project)
def project_profile_updated(sender, instance, created, **kwargs):
    """
    Notifies investors when a Project profile is updated.

    Args:
        sender (Model): The model class that triggered the signal.
        instance (Project): The instance of the Project that was saved.
        created (bool): A boolean indicating whether a new instance was created.
        **kwargs: Additional keyword arguments.
    """
    if InvestorProject.objects.filter(project=instance):
        trigger = 'Project profile changed'
        addressees = Investor.objects.filter(shortlisted_project__project=instance)
        for addressee in addressees:
            email_prefs_list = [pref.strip() for pref in addressee.investor_notice_prefs.active_email_preferences.split(',')]
            push_prefs_list = [pref.strip() for pref in addressee.investor_notice_prefs.active_push_preferences.split(',')]
            if trigger in email_prefs_list or trigger in push_prefs_list:
                notifications = []
                notification = Notification(
                    project = instance,
                    startup = instance.startup,
                    investor = addressee,
                    trigger = trigger,
                    initiator = 'project'
                )
                notifications.append(notification)
        if notifications:
            record_notifications(notifications)
            send_notifications(notifications)

@receiver(post_save, sender=SubscribeInvestorStartup)
@receiver(post_delete, sender=SubscribeInvestorStartup)
def startup_followed(sender, instance, created=None, **kwargs):
    """
    Notifies the Startup when an investor subscribes or unsubscribes.

    Args:
        sender (Model): The model class that triggered the signal.
        instance (SubscribeInvestorStartup): The instance of the subscription that was saved or deleted.
        created (bool, optional): A boolean indicating whether a new instance was created.
        **kwargs: Additional keyword arguments.
    """
    trigger = 'Startup subscribers list changed'
    addressee = instance.startup
    email_prefs_list = [pref.strip() for pref in addressee.startup_notice_prefs.active_email_preferences.split(',')]
    push_prefs_list = [pref.strip() for pref in addressee.startup_notice_prefs.active_push_preferences.split(',')]
    if trigger in email_prefs_list or trigger in push_prefs_list:
        notification = Notification(
            startup = addressee,
            investor = instance.investor,
            trigger = trigger,
            initiator = 'investor'
        )
        record_notifications([notification])
        send_notifications([notification])

@receiver(post_save, sender=InvestorProject)
@receiver(post_delete, sender=InvestorProject)
def project_followed_or_subscription_status_changed(sender, instance, created=None, **kwargs):
    """
    Notifies the Startup when an investor follows or unfollows a project or when subscription share changes.

    Args:
        sender (Model): The model class that triggered the signal.
        instance (InvestorProject): The instance of the project follow or subscription that was saved or deleted.
        created (bool, optional): A boolean indicating whether a new instance was created.
        **kwargs: Additional keyword arguments.
    """
    trigger = 'Project follower list or subscription share change'
    addressee = instance.project.startup
    email_prefs_list = [pref.strip() for pref in addressee.startup_notice_prefs.active_email_preferences.split(',')]
    push_prefs_list = [pref.strip() for pref in addressee.startup_notice_prefs.active_push_preferences.split(',')]
    if trigger in email_prefs_list or trigger in push_prefs_list:
        notification = Notification(
            project = instance.project,
            startup = addressee,
            investor = instance.investor,
            trigger = trigger,
            initiator = 'investor'
        )
        record_notifications([notification])
        send_notifications([notification])
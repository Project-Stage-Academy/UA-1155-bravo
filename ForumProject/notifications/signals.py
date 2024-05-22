from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Notification
from projects.models import InvestorProject
from startups.models import Startup
from django.core.exceptions import ValidationError
from django.core.mail import send_mail

from users.models import UserStartup
from .utils import send_email_async

from django.db import DatabaseError
from django.conf import settings
import logging
import threading

logger = logging.getLogger(__name__)

def create_notifications(instances, follow_status_change=True):
    """
    Creates Notification records for the provided InvestorProject instance(s).

    Args:
    - instances (InvestorProject or list[InvestorProject]): The InvestorProject instance(s) for which 
      to create notifications.
    - follow_status_change (bool, optional): True if the trigger is a change in the following status, 
      False if the trigger is a change in subscription share. Defaults to True.

    Returns:
    - list[Notification]: List of created Notification instances.
    """
    if not isinstance(instances, list):
        instances = [instances]

    notifications = []
    for instance in instances:
        # Validate fields
        if not instance.project or not instance.project.startup or not instance.investor:
            raise ValidationError("Invalid InvestorProject instance. Ensure project, startup, and investor are valid.")

        # Add to the list of notifications to be created
        notifications.append(
            Notification(
                project=instance.project,
                startup=instance.project.startup,
                investor=instance.investor,
                trigger='Project follower(s) list changed' if follow_status_change else 'Project subscription changed',
                initiator='investor',
            )
        )

    try:
        # Bulk create all notifications
        if notifications:
            return Notification.objects.bulk_create(notifications)
    except DatabaseError as db_err:
        logger.error(f"Database error while creating notifications: {str(db_err)}")

    return notifications

def do_notifications(instance, follow_status_change=True):
    """
    Creates Notification records and sends email notifications for a given InvestorProject instance.

    Args:
    - instance (InvestorProject): The InvestorProject instance for which to create and send notifications.
    - follow_status_change (bool, optional): True if the trigger is a change in the following status, 
      False if it's a change in subscription share. Defaults to True.
    """
    # Get all CustomUsers' emails associated with this startup
    project = instance.project
    startup = project.startup
    user_startups = UserStartup.objects.select_related('customuser').filter(startup=startup)
    recipients = [user.customuser.email for user in user_startups if user.customuser.email]

    #trigger recording of notifications to the database
    notifications = create_notifications(instance, follow_status_change=follow_status_change)
    
    if recipients and notifications:
        # prepare data for email
        change = 'follower(s) list' if follow_status_change else 'subscription'
        subject = f'The Project "{project.name}" has a change in {change}.'
        message = f'{str(notifications[0])}.\n\n\n{str(instance)}'

        if follow_status_change:
            if startup.startup_notice_prefs.email_project_followers_change:
                # Asynchronously send email
                email_thread = threading.Thread(target=send_email_async, args=(subject, message, recipients))
                email_thread.start()
            if startup.startup_notice_prefs.push_project_followers_change:
                print(message) # This is a placeholder for "in app" / push notifications implementation
        else:
            if startup.startup_notice_prefs.email_project_subscription_change:
                # Asynchronously send email
                email_thread = threading.Thread(target=send_email_async, args=(subject, message, recipients))
                email_thread.start()
            if startup.startup_notice_prefs.push_project_subscription_change:
                print(message) # This is a placeholder for "in app" / push notifications implementation

# Signal to record and send a notification when an investor starts following a project or changes a share
@receiver(post_save, sender=InvestorProject)
def project_followed_or_subscription_changed(sender, instance, created, **kwargs):
    """
    Signal handler to create Notification records and send email notifications when an 
    InvestorProject is created or updated.

    Args:
    - sender (type): The model class that sent the signal.
    - instance (InvestorProject): The InvestorProject instance that triggered the signal.
    - created (bool): Whether the `InvestorProject` instance was just created.
    """
    if created:
        # Investor just started following a project (share is initialized to 0 or another value)
        do_notifications(instance)
        if instance.share:
            do_notifications(instance, follow_status_change=False)
    else:
        # Investor changed the share (subscription)
        do_notifications(instance, follow_status_change=False)

# Signal to record and send a notification when an investor delists a project
@receiver(post_delete, sender=InvestorProject)
def project_delisted(sender, instance, **kwargs):
    """
    Signal handler to create a Notification record and send email notifications when an InvestorProject is deleted.

    Args:
    - sender (type): The model class that sent the signal.
    - instance (InvestorProject): The InvestorProject instance that triggered the signal.
    """
    instance.__class__.__str__ = lambda self: 'The Investor has stopped following this Project'
    do_notifications(instance)
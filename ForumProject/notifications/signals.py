from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Notification
from projects.models import InvestorProject
from django.core.exceptions import ValidationError
from django.core.mail import send_mail

from users.models import UserStartup
from .utils import send_notification_email

def create_notifications(instances, follow_status_change=True):
    """
    Creates Notification records for the provided InvestorProject instances.

    Parameters:
    - instances: A single InvestorProject instance or a list of them.
    - follow_status_change (bool): Whether the trigger is a change in the following status
      (default: True). If False, the trigger is considered a change in the subscription share.

    Returns:
    - List of created Notification instances.
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
                trigger='follower(s) list changed' if follow_status_change else 'subscription changed',
                initiator='investor',
            )
        )

    # Bulk create all notifications
    if notifications:
        return Notification.objects.bulk_create(notifications)
    return []

def record_and_email_notifications(instance, follow_status_change=True):
    """
    Create Notification records and send email notifications for a given InvestorProject instance.

    This function creates Notification records in the database and sends email notifications
    to CustomUsers associated with the startup linked to the InvestorProject instance.

    Parameters:
    - instance (InvestorProject): The InvestorProject instance to process.
    - follow_status_change (bool): Whether the trigger is a change in the following status
      (default: True). If False, it is considered a change in the subscription share.
    """
    #trigger recording of notifications to the database
    notifications = create_notifications(instance, follow_status_change=follow_status_change)
    
    for notification in notifications:
        # Get all CustomUsers' emails associated with this startup
        project = instance.project
        startup = project.startup
        user_startups = UserStartup.objects.filter(startup=startup)
        recipients = [user.customuser.email for user in user_startups]

        if recipients:
            # prepare data for email
            change = 'follower(s) list' if follow_status_change else 'subscription'
            subject = f'The Project "{project.name}" has a change in {change}.'
            message = f'{str(notification)}.\n\n\n{str(instance)}'
            # send email
            send_notification_email(subject, message, recipients)

# Signal to record and send a notification when an investor starts following a project or changes a share
@receiver(post_save, sender=InvestorProject)
def investor_project_followed_or_subscription_changed(sender, instance, created, **kwargs):
    """
    Signal handler to create Notification records and send email notifications when an InvestorProject is
    created or updated.

    If the instance is created, this indicates that an investor has started following a project.
    If the instance is updated, it indicates a change in the subscription share.

    Parameters:
    - sender (type): The model class that sent the signal (usually `InvestorProject`).
    - instance (InvestorProject): The InvestorProject instance that triggered the signal.
    - created (bool): Whether the `InvestorProject` instance was just created.
    """
    if created:
        # Investor just started following a project (share is initialized to 0 or another value)
        record_and_email_notifications(instance)
    else:
        # Investor changed the share (subscription)
        record_and_email_notifications(instance, follow_status_change=False)

# Signal to record and send a notification when an investor delists a project
@receiver(post_delete, sender=InvestorProject)
def investor_project_delisted(sender, instance, **kwargs):
    """
    Signal handler to create a Notification record and send email notifications when an InvestorProject is deleted.

    This signal is triggered when an investor delists a project, indicating they have stopped following it.

    Parameters:
    - sender (type): The model class that sent the signal.
    - instance (InvestorProject): The InvestorProject instance that triggered the signal.
    """
    record_and_email_notifications(instance)

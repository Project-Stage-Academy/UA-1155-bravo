from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Notification
from projects.models import InvestorProject
from django.core.exceptions import ValidationError

def create_notifications(instances, follow_status_change=True):
    """
    Creates Notification records for the provided InvestorProject instances.

    This function creates Notification records either for a single InvestorProject instance
    or for multiple instances in bulk.

    Parameters:
    - instances: A single InvestorProject instance or a list of them.
    - follow_status_change (bool): Whether the trigger is a change in the following status.
      If False, the trigger is considered a change in the subscription share.

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

# Signal to create a notification when an investor starts following a project or changes a share
@receiver(post_save, sender=InvestorProject)
def investor_project_followed_or_subscription_changed(sender, instance, created, **kwargs):
    """
    Signal handler to create notifications when an InvestorProject is created or updated.

    This signal is triggered when an investor starts following a project or changes their 
    subscription share in a project. It creates a `Notification` record indicating whether 
    the trigger was due to following status or subscription share.

    Parameters:
    - sender (type): The model class that sent the signal (usually `InvestorProject`).
    - instance (InvestorProject): The instance that triggered the signal.
    - created (bool): Whether the `InvestorProject` instance was just created.
    - kwargs (dict): Additional arguments for the signal handler.
    """
    if created:
        # Investor just started following a project (share is initialized to 0 or another value)
        create_notifications(instance)
    else:
        # Investor changed the share (subscription)
        create_notifications(instance, follow_status_change=False)

# Signal to create a notification when an investor delists a project
@receiver(post_delete, sender=InvestorProject)
def investor_project_delisted(sender, instance, **kwargs):
    """
    Signal handler that creates a notification when an `InvestorProject` record is deleted.

    This signal is triggered when an investor delists a project, indicating that they 
    have stopped following the project. It creates a `Notification` record to represent 
    this change.

    Parameters:
    - sender (type): The model class that sent the signal (usually `InvestorProject`).
    - instance (InvestorProject): The instance that triggered the signal.
    - kwargs (dict): Additional arguments for the signal handler.
    """
    create_notifications(instance)

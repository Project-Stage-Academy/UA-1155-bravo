from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Notification
from projects.models import InvestorProject

def create_notification(instance, follow_status_change=True):
    '''
    Helper function.
    Create a new `Notification` record based on the `InvestorProject` instance.

    This function creates a `Notification` record that represents a change in the 
    relationship between an investor and a project. The trigger for the notification 
    depends on whether it's a change in the following status or subscription share.

    Parameters:
    - instance (InvestorProject): The `InvestorProject` instance that triggered the notification.
    - follow_status_change (bool): Whether the trigger is a change in the following status. 
      Default is True. If False, the trigger is considered a change in the subscription share.
    
    Returns:
    - Notification: The created `Notification` instance.
    '''
    Notification.objects.create(
            project=instance.project,
            startup=instance.project.startup,
            investor=instance.investor,
            trigger='follower(s) list changed' if follow_status_change else 'subscription changed',
            initiator='investor',
        )

# Signal to create a notification when an investor starts following a project or changes a share
@receiver(post_save, sender=InvestorProject)
def investor_project_followed_or_subscription_changed(sender, instance, created, **kwargs):
    '''
    Signal handler that creates a notification when an `InvestorProject` record is created or updated.

    This signal is triggered when an investor starts following a project or changes their 
    subscription share in a project. It creates a `Notification` record indicating whether 
    the trigger was due to following status or subscription share.

    Parameters:
    - sender (type): The model class that sent the signal (usually `InvestorProject`).
    - instance (InvestorProject): The instance that triggered the signal.
    - created (bool): Whether the `InvestorProject` instance was just created.
    - kwargs (dict): Additional arguments for the signal handler.
    '''

    if created:
        # Investor just started following a project (share is initialized to 0 or another value)
        create_notification(instance)
    else:
        # Investor changed the share (subscription)
        create_notification(instance, follow_status_change=False)

# Signal to create a notification when an investor delists a project
@receiver(post_delete, sender=InvestorProject)
def investor_project_delisted(sender, instance, **kwargs):
    '''
    Signal handler that creates a notification when an `InvestorProject` record is deleted.

    This signal is triggered when an investor delists a project, indicating that they 
    have stopped following the project. It creates a `Notification` record to represent 
    this change.

    Parameters:
    - sender (type): The model class that sent the signal (usually `InvestorProject`).
    - instance (InvestorProject): The instance that triggered the signal.
    - kwargs (dict): Additional arguments for the signal handler.
    '''
    create_notification(instance)

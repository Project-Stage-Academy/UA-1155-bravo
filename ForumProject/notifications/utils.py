from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_notification_email(subject, message, recipient_list):
    """
    Send a notification email to a list of recipients.
    
    Parameters:
    - subject (str): The subject of the email.
    - message (str): The body content of the email.
    - recipient_list (list): List of email addresses to send to.
    """
    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            recipient_list,
            fail_silently=False
        )
    except Exception as e:
        logger.error(f"Failed to send email to {len(recipient_list)} recipients: {str(e)}")
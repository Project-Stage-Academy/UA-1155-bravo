from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMessage
import logging

logger = logging.getLogger(__name__)

def send_email_async(subject, message, recipients):
    """
    Sends email notifications asynchronously.

    Args:
    - subject (str): The subject of the email.
    - message (str): The body of the email.
    - recipients (list[str]): List of email addresses to send to.
    """
    try:
        email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, recipients)
        email.send()
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}; Subject: {subject}; Recipients: {recipients}")
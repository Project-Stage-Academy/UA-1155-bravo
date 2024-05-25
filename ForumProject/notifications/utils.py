"""
Utility for sending email notifications asynchronously.

This module defines a function for sending email notifications and handles potential
errors during the process.

Functions:
    send_email_async: Sends email notifications asynchronously.
"""

import logging
from django.conf import settings
from django.core.mail import EmailMessage

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

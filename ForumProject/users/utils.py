import logging

from django.conf import settings
from django.core.mail import EmailMessage
from rest_framework.reverse import reverse

logger = logging.getLogger('django.server')


class Util:
    """
    A utility class for sending emails.

    This class provides a static method to send an email for user verification.

    Methods:
    - send_email: Sends an email with a verification link to the user.
    """
    @staticmethod
    def send_email(site, view_name, user, token, message_data):
        """
        Send an email with a verification link to the user.
SS
        Parameters:
        - site (str): The domain of the website.
        - view_name (str): The name of the view.
        - user (CustomUser): The user object.
        - token (str): The verification token.
        - message_data (dict): The dict with subject and body for email.

        Returns:
        - None

        Sends an email to the user's email address containing a verification link.
        """
        verification_link = reverse(view_name, kwargs={'token': str(token)})
        absolute_url = site + verification_link
        email = EmailMessage(
            subject=message_data['subject'],
            body='Hi ' + user.first_name + message_data['body'] + absolute_url,
            from_email=settings.EMAIL_HOST_USER,
            to=[user.email]
        )
        try:
            email.send()
        except Exception as e:
            logging.error(f"Failed to send email to {user.email}: {str(e)}")

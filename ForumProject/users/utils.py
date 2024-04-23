from django.conf import settings
from django.core.mail import EmailMessage
from rest_framework.reverse import reverse


class Util:
    """
    A utility class for sending emails.

    This class provides a static method to send an email for user verification.

    Methods:
    - send_email: Sends an email with a verification link to the user.
    """
    @staticmethod
    def send_email(site, user, token):
        """
        Send an email with a verification link to the user.
SS
        Parameters:
        - site (str): The domain of the website.
        - user (CustomUser): The user object.
        - token (str): The verification token.

        Returns:
        - None

        Sends an email to the user's email address containing a verification link.
        """
        verification_link = reverse('users:email-verify', kwargs={'token': str(token)})
        absolute_url = 'http://' + site + verification_link
        email = EmailMessage(
            subject='Verify your email',
            body='Hi ' + user.first_name + ' Use the link below to verify your email \n' + absolute_url,
            from_email=settings.EMAIL_HOST_USER,
            to=[user.email]
        )
        email.send()

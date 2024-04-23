from django.conf import settings
from django.core.mail import EmailMessage
from rest_framework.reverse import reverse


class Util:
    @staticmethod
    def send_email(site, user, token):
        verification_link = reverse('users:email-verify', kwargs={'token': str(token)})
        absolute_url = 'http://' + site + verification_link
        email = EmailMessage(
            subject='Verify your email',
            body='Hi ' + user.first_name + ' Use the link below to verify your email \n' + absolute_url,
            from_email=settings.EMAIL_HOST_USER,
            to=[user.email]
        )
        email.send()

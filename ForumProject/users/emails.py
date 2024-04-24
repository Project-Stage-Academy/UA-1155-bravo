def send_password_reset_email(email, reset_url):
    subject = 'Password Reset Request'
    message = f'Click the link to reset your password: {reset_url}'
    send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)

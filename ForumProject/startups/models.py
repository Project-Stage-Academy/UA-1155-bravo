from django.db import models
from django.core.exceptions import ValidationError
from .validation import phone_regex, image_validator
from django_countries.fields import CountryField
from notifications.models import Notification


class Startup(models.Model):
    """
    Model representing a startup.

    Attributes:
        startup_name (str): The name of the startup.
        startup_industry (str): The industry of the startup.
        startup_phone (str): The phone number of the startup.
        startup_country (CountryField): The country where the startup is located.
        startup_city (str): The city where the startup is located.
        startup_address (str): The address of the startup.
        startup_logo (ImageField): The logo of the startup.
    """
    
    startup_name = models.CharField(max_length=150, unique=True) 
    startup_industry = models.CharField(max_length=50)
    startup_phone = models.CharField(max_length=20, validators=[phone_regex])
    startup_country = CountryField()
    startup_city = models.CharField(max_length=50)
    startup_address = models.CharField(max_length=150)
    startup_logo = models.ImageField(upload_to='media/startup_logos/', validators=[image_validator], null=True, blank=True)


    def __str__(self):
        """
        Return the name of the startup.
        
        Returns:
            str: The name of the startup.
        """
        
        return self.startup_name

    def clean(self):
        """
        Validate that all required fields are filled in.
        
        Raises:
            ValidationError: If any required field is empty.
        """
        
        if not self.startup_name or not self.startup_industry or not self.startup_phone or not self.startup_city or not self.startup_address:
            raise ValidationError("All fields must be filled in: name, industry, phone, country, city, address.")

class NotificationPreference(models.Model):
    """
    Model representing notification preferences for each type.

    Attributes:
        startup (ForeignKey): Reference to the startup associated with the notification preferences.
        notification_type (str): The type of notification.
        email_notification (bool): Whether email notifications are enabled for the notification type.
        in_app_notification (bool): Whether in-app notifications are enabled for the notification type.
    """
    startup = models.OneToOneField('Startup', on_delete=models.CASCADE, related_name='notification_preferences')
    notification_type = models.CharField(max_length=50, choices=Notification.TRIGGER_CHOICES)
    email_notification = models.BooleanField(default=True)
    in_app_notification = models.BooleanField(default=True)
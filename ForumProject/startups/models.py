from django.db import models
from users.models import CustomUser
from django_countries.fields import CountryField
from phonenumber_field.phonenumber import PhoneNumberField

class Startup(models.Model):
    startup_id = models.BigAutoField(primary_key=True)
    startup_name = models.CharField(max_length=100)
    startup_logo = models.ImageField(upload_to='logos/')
    startup_industry = models.CharField(max_length=20)
    startup_phone = PhoneNumberField(region='ua')
    startup_country = CountryField()
    startup_city = models.CharField(max_length=28)
    startup_address = models.CharField(max_length=95)


    def __str__(self):
        return self.startup_name

class UserStartup(models.Model):
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    startup_id = models.ForeignKey(Startup, on_delete=models.CASCADE)
    # startup_role_id =

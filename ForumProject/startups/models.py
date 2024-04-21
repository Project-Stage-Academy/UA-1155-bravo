from django.db import models
from django.core.exceptions import ValidationError
from .validation import phone_regex, image_validator
from django_countries.fields import CountryField



class Startup(models.Model):
    startup_name = models.CharField(max_length=150, unique=True) 
    startup_industry = models.CharField(max_length=50)
    startup_phone = models.CharField(max_length=20, validators=[phone_regex])
    startup_country = CountryField()
    startup_city = models.CharField(max_length=50)
    startup_address = models.CharField(max_length=150)
    startup_logo = models.ImageField(upload_to='media/startup_logos/', validators=[image_validator], null=True, blank=True)
    id = models.AutoField(primary_key=True)
    # add ForeignKey (link to UserStartup) ?
    # add ForeignKey (link to Project) ?

    def __str__(self):
        return self.startup_name
    
    # Validate non-empty startup_name
    def clean(self):
        if not self.startup_name or not self.startup_industry or not self.startup_phone or not self.startup_city or not self.startup_address:
            raise ValidationError("All fields must be filled in: name, industry, phone, country, city, address.")
        
    
 

from django.db import models
from django.core.exceptions import ValidationError

class Startup(models.Model):
    startup_name = models.CharField(max_length=150, unique=True)
    # startup_logo = 
    startup_industry = models.CharField(max_length=50)
    startup_phone = models.CharField(max_length=20)
    startup_country = models.CharField(max_length=50)
    startup_city = models.CharField(max_length=50)
    startup_address = models.CharField(max_length=150)
    # add ForeignKey (link to UserStartup) ?
    # add ForeignKey (link to Project) ?

    def __str__(self):
        return self.startup_name
    
    # Validate non-empty startup_name
    def clean(self):
        if not self.startup_name:
            raise ValidationError("Startup name cannot be empty.")

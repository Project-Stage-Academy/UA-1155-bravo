from django.db import models

class Startup(models.Model):
    startup_name = models.CharField(max_length=150)
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

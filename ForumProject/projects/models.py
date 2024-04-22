from django.db import models
from django.core.exceptions import ValidationError
from startups.models import Startup


class Project(models.Model):
    
    project_name = models.CharField(max_length=150, unique=True)
    startup_id = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name='projects')
    PROJECT_STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('pending', 'Pending'),
    ]
    project_status = models.CharField(max_length=20, choices=PROJECT_STATUS_CHOICES, default='open')
    id = models.AutoField(primary_key=True)
    

    def __str__(self):
        return self.project_name



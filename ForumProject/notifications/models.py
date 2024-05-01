from django.db import models
from projects.models import Project
from investors.models import Investor

class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE)
    trigger = models.CharField(max_length=255)

    def __str__(self):
        return f'Notification ID: {self.notification_id}'

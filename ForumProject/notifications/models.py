from django.db import models
from projects.models import Project
from investors.models import Investor
from startups.models import Startup

class Notification(models.Model):
    
    TRIGGER_CHOICES = [
        ('follower(s) list changed', 'follower(s) list changed'),
        ('subscription changed', 'subscription changed'),
        ('project status changed', 'project status changed'),
        ('project budget changed', 'project budget changed'),
        ('message sent', 'message sent'),
    ]
    INITIATOR_CHOICES = [
        ('investor', 'investor'),
        ('project', 'project'),
    ]    
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, related_name='notice_on_project')
    startup_name = models.CharField(max_length=Startup._meta.get_field('startup_name').max_length)
    investor = models.ForeignKey(Investor, on_delete=models.SET_NULL, related_name='notice_to_investor')
    trigger = models.CharField(max_length=50, choices=TRIGGER_CHOICES)
    initiator = models.CharField(max_length=8, choices=INITIATOR_CHOICES)
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        addressee = f'Startup {self.startup_name}' if self.initiator == 'investor' else f'Investor {self.investor.investor_name}'
        return f'Notification of {self.date_time} to {addressee} on Project {self.project.project_name}'
        # the above line to be replaced with the below as field project.project_name is being replaced with project.name
        # return f'Notification of {self.date_time} to {addressee} on Project {self.project.project_name}'

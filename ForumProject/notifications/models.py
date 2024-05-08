from django.db import models
from projects.models import Project
from investors.models import Investor
from startups.models import Startup

class Notification(models.Model):
    # Choices for the trigger field
    TRIGGER_CHOICES = [
        ('follower(s) list changed', 'follower(s) list changed'),
        ('subscription changed', 'subscription changed'),
        ('project status changed', 'project status changed'),
        ('project budget changed', 'project budget changed'),
        ('message sent', 'message sent'),
    ]
    # Choices for the initiator field
    INITIATOR_CHOICES = [
        ('investor', 'investor'),
        ('project', 'project'),
    ]    
    # ForeignKey to Project model
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, related_name='notice_project', null=True)
    # ForeignKey to Startup model
    startup = models.ForeignKey(Startup, on_delete=models.SET_NULL, related_name='notice_startup', null=True)
    # ForeignKey to Investor model
    investor = models.ForeignKey(Investor, on_delete=models.SET_NULL, related_name='notice_investor', null=True)
    # CharField for trigger choice
    trigger = models.CharField(max_length=50, choices=TRIGGER_CHOICES)
    # CharField for initiator choice
    initiator = models.CharField(max_length=8, choices=INITIATOR_CHOICES)
    # DateTimeField for date and time
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Define addressee based on initiator choice
        addressee = 'Unknown'
        if self.initiator == 'investor':
            addressee = f'Startup {self.project.startup.startup_name}'
        else:
            addressee = f'Investor {self.investor.investor_name}'
        # Return notification string
        return f'Notification of {self.date_time} to {addressee} on Project {self.project.name}'

    class Meta:
        # Add model-level constraint
        constraints = [
            models.CheckConstraint(check=models.Q(project__isnull=False) | models.Q(investor__isnull=False), name='project_or_investor_required'),
        ]
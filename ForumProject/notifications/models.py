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
    # ForeignKey to Project model with null=True and blank=True parameters
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, related_name='notice_on_project', null=True, blank=True)
    # CharField for startup name
    startup_name = models.CharField(max_length=Startup._meta.get_field('startup_name').max_length)
    # ForeignKey to Investor model with null=True and blank=True parameters
    investor = models.ForeignKey(Investor, on_delete=models.SET_NULL, related_name='notice_to_investor', null=True, blank=True)
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
            if self.investor:
                addressee = f'Investor {self.investor.investor_name}'
        elif self.project:
            addressee = f'Startup {self.startup_name}'
        # Return notification string
        return f'Notification of {self.date_time} to {addressee} on Project {self.project.name if self.project else "N/A"}'

    class Meta:
        # Add model-level constraint
        constraints = [
            models.CheckConstraint(check=models.Q(project__isnull=False) | models.Q(investor__isnull=False), name='project_or_investor_required'),
        ]

class NotificationPreference(models.Model):
    new_follows = models.BooleanField(default=True)
    new_messages = models.BooleanField(default=True)
    project_updates = models.BooleanField(default=True)

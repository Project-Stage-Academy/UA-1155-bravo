from django.db import models
from projects.models import Project
from investors.models import Investor
from startups.models import Startup

class Notification(models.Model):
    # Choices for the trigger field
    TRIGGER_CHOICES = [
        # with these triggers, Project owners should receive Notification
        ('Project follower(s) list changed', 'Project follower(s) list changed'),
        ('Project subscription changed', 'Project subscription changed'),
        # with this trigger, owners of Investors that follow Project should receive Notification
        ('Project profile changed', 'Project profile changed'),
        # with this trigger, owners of Investors that subscribed for Startup should receive a Notification
        ('Startup profile updated', 'Startup profile updated'),
        # with these triggers, Startup owners should receive a Notification
        ('Startup got new sibscriber', 'Startup got new sibscriber'),
        ('Startup has lost a sibscriber', 'Startup has lost a sibscriber'),
    ]
    # Choices for the initiator field
    INITIATOR_CHOICES = [
        ('investor', 'investor'),
        ('project', 'project'),
        ('startup', 'startup'),
    ]    
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, related_name='notice_project', null=True)
    startup = models.ForeignKey(Startup, on_delete=models.SET_NULL, related_name='notice_startup', null=True)
    investor = models.ForeignKey(Investor, on_delete=models.SET_NULL, related_name='notice_investor', null=True)
    trigger = models.CharField(max_length=50, choices=TRIGGER_CHOICES)
    initiator = models.CharField(max_length=8, choices=INITIATOR_CHOICES)
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        addressee = 'Unknown'
        project_name = self.project.name if self.project else None
        startup_name = self.startup.startup_name if self.startup else None
        investor_name = self.investor.investor_name if self.investor else None

        if self.initiator == 'investor':
            addressee = f'Startup {startup_name}' if startup_name else 'Unknown'
        elif self.initiator == 'project':
            addressee = f'Investor {investor_name}' if investor_name else 'Unknown'
        elif self.initiator == 'startup':
            addressee = f'Investor {investor_name}' if investor_name else 'Unknown'

        return f'Notification of {self.date_time} to {addressee} on Project {project_name}'



    class Meta:
        # Add model-level constraint
        constraints = [
            models.CheckConstraint(check=models.Q(project__isnull=False) | models.Q(investor__isnull=False), name='project_or_investor_required'),
        ]

class StartupNotificationPrefs(models.Model):
    startup = models.OneToOneField(
        Startup, 
        on_delete=models.CASCADE,
        related_name='startup_notice_prefs',
        null=True
    )
    # preferences for Notifications about Investors' actions on PROJECTS
    email_project_followers_change = models.BooleanField(default=True, verbose_name='Email on Project followers change')
    email_project_subscription_change = models.BooleanField(default=True, verbose_name='Email on Project subscription change')
    push_project_followers_change = models.BooleanField(default=True, verbose_name='Push on Project followers change')
    push_project_subscription_change = models.BooleanField(default=True, verbose_name='Push on Project subscription change')
    # preferences for Notifications about Investors' actions on STARTUPS
    email_startup_subscribed = models.BooleanField(default=True, verbose_name='Email if Startup subscribed')
    email_startup_unsubscribed = models.BooleanField(default=True, verbose_name='Email if Startup unsubscribed')
    push_startup_subscribed = models.BooleanField(default=True, verbose_name='Push if Startup subscribed')
    push_startup_unsubscribed = models.BooleanField(default=True, verbose_name='Push if Startup unsubscribed')

class InvestorNotificationPrefs(models.Model):
    investor = models.OneToOneField(
        Investor,
        on_delete=models.CASCADE,
        related_name='investor_notice_prefs',
        null=True
    )
    # preferences for Notifications about Startups' actions on PROJECTS
    email_project_profile_change = models.BooleanField(default=True, verbose_name='Email if Project profile changes')
    push_project_profile_change = models.BooleanField(default=True, verbose_name='Push if Project profile changes')
    
    # preferences for Notifications about Startups' actions on STARTUPS
    email_startup_profile_update = models.BooleanField(default=True, verbose_name='Email if Startup profile updates')
    push_startup_profile_update = models.BooleanField(default=True, verbose_name='Push if Startup profile updates')

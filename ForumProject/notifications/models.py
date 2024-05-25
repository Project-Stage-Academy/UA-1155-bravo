"""
Module for models related to notifications.

This module contains models for notifications and their associated preferences.

Classes:
    Notification: Model for storing notifications.
    StartupNotificationPrefs: Model for storing notification preferences for startups.
    InvestorNotificationPrefs: Model for storing notification preferences for investors.
"""

from django.db import models
from projects.models import Project
from investors.models import Investor
from startups.models import Startup


class Notification(models.Model):
    # Choices for the trigger field
    TRIGGER_CHOICES = [
        # with this trigger, Project owners should receive Notification
        ('Project follower list or subscription share change', 'Project follower list or '
                                                               'subscription share change'),
        # with this trigger, owners of Investors that follow Project should receive Notification
        ('Project profile changed', 'Project profile changed'),
        # with this trigger, owners of Investors that subscribed for Startup should receive a
        # Notification
        ('Startup profile updated', 'Startup profile updated'),
        # with this trigger, Startup owners should receive a Notification
        ('Startup subscribers list changed', 'Startup subscribers list changed'),
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
    trigger = models.CharField(max_length=55, choices=TRIGGER_CHOICES)
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
    email_project_on_investor_interest_change = models.BooleanField(default=True, verbose_name='Email Investor-Project interest')
    push_project_on_investor_interest_change = models.BooleanField(default=True, verbose_name='Push Investor-Project interest')
    # preferences for Notifications about Investors' actions on STARTUPS
    email_startup_on_investor_interest_change = models.BooleanField(default=True, verbose_name='Email Investor-Startup interest')
    push_startup_on_investor_interest_change = models.BooleanField(default=True, verbose_name='Push Investor-Startup interest')

    active_email_preferences = models.CharField(
        max_length=100, 
        blank=True, 
        default='Project follower list or subscription share change, Startup subscribers list changed'
    )
    active_push_preferences = models.CharField(
        max_length=100, 
        blank=True, 
        default='Project follower list or subscription share change, Startup subscribers list changed'
    )

    def update_active_preferences(self):
        email_preferences = []
        push_preferences = []
        if self.email_project_on_investor_interest_change:
            email_preferences.append('Project follower list or subscription share change')
        if self.email_startup_on_investor_interest_change:
            email_preferences.append('Startup subscribers list changed')
        if self.push_project_on_investor_interest_change:
            push_preferences.append('Project follower list or subscription share change')
        if self.push_startup_on_investor_interest_change:
            push_preferences.append('Startup subscribers list changed')
        self.active_email_preferences = ', '.join(email_preferences)
        self.active_push_preferences = ', '.join(push_preferences)

    def save(self, *args, **kwargs):
        self.update_active_preferences()
        super().save(*args, **kwargs)


class InvestorNotificationPrefs(models.Model):
    investor = models.OneToOneField(
        Investor,
        on_delete=models.CASCADE,
        related_name='investor_notice_prefs',
        null=True
    )
    # preferences for Notifications about Startups' actions on PROJECTS
    email_project_profile_change = models.BooleanField(default=True, verbose_name='Email Project changes')
    push_project_profile_change = models.BooleanField(default=True, verbose_name='Push Project changes')
    
    # preferences for Notifications about Startups' actions on STARTUPS
    email_startup_profile_update = models.BooleanField(default=True, verbose_name='Email Startup updates')
    push_startup_profile_update = models.BooleanField(default=True, verbose_name='Push Startup updates')

    active_email_preferences = models.CharField(
        max_length=50, 
        blank=True, 
        default='Project profile changed, Startup profile updated'
    )
    active_push_preferences = models.CharField(
        max_length=50, 
        blank=True, 
        default='Project profile changed, Startup profile updated'
    )

    def update_active_preferences(self):
        email_preferences = []
        push_preferences = []
        if self.email_project_profile_change:
            email_preferences.append('Project profile changed')
        if self.email_startup_profile_update:
            email_preferences.append('Startup profile updated')
        if self.push_project_profile_change:
            push_preferences.append('Project profile changed')
        if self.push_startup_profile_update:
            push_preferences.append('Startup profile updated')
        self.active_email_preferences = ', '.join(email_preferences)
        self.active_push_preferences = ', '.join(push_preferences)

    def save(self, *args, **kwargs):
        self.update_active_preferences()
        super().save(*args, **kwargs)

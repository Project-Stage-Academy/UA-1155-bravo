from django.db import models
from django.core.exceptions import ValidationError
from startups.models import Startup
from investors.models import Investor


class Project(models.Model):
    """
    Model representing a project.

    Attributes:
        project_name (str): The name of the project.
        startup (ForeignKey): The startup associated with the project.
        project_status (str): The status of the project, chosen from predefined choices.
        
    Note: This model is not finished yet.
    """
    
    project_name = models.CharField(max_length=150, unique=True)
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name='projects')
    PROJECT_STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('pending', 'Pending'),
    ]
    project_status = models.CharField(max_length=20, choices=PROJECT_STATUS_CHOICES, default='open')

    def __str__(self):
        """
        Return the name of the project.
        
        Returns:
            str: The name of the project.
        """
        return self.project_name


class InvestorProject(models.Model):
    """
    Model represents the relationship between an Investor and a Project,
    including the percentage share the Investor holds in the Project.
    """
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    share = models.IntegerField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(share__gte=0) & models.Q(share__lte=100),
                name='percentage_share_range'
            )
        ]

    def clean(self):
        """
        Validates the InvestorProject instance.

        Ensures that the share is within the valid range (0-100).
        """
        if self.share < 0 or self.share > 100:
            raise ValidationError("Share percentage must be between 0 and 100.")

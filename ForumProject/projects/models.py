from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from startups.models import Startup
from investors.models import Investor
import os
import logging
from datetime import datetime


logger = logging.getLogger(__name__)


class Project(models.Model):
    """
    Model representing a project.

    Attributes:
        name (str): The name of the Project.
        startup (ForeignKey): The startup associated with the Project.
        description (str): A description of the Project (up to 500 characters).
        documentation (files): Files relating to the Project that can be uploaded.
        status (str): The status of the Project, chosen from predefined choices.
        created_at (date-time): date of creation of the Project.
        updated_at (date-time): date of last modification of the Project.
        duration (float): number of months which implementation of the Project is planned for.
        budget_currency (str): currency of the Project's budget
        budget_amount (int): amount of the Project's budget
    """
    name = models.CharField(max_length=150, db_index=True)
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name='projects')
    description = models.CharField(max_length=500, db_index=True)
    PROJECT_STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('pending', 'Pending'),
    ]
    status = models.CharField(max_length=20, choices=PROJECT_STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    duration = models.FloatField(blank=True, null=True, verbose_name='duration (months)')
    budget_currency = models.CharField(max_length=3, blank=True, null=True)
    budget_amount = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        ordering = ['startup', 'name']
        constraints = [
            models.UniqueConstraint(fields=['startup', 'name'], name='unique_project_per_startup')
        ]

    def __str__(self):
        """
        Return the name of the project.
        
        Returns:
            str: The name of the project.
        """
        return self.name


class ProjectFiles(models.Model):

    def _generate_upload_path(self, filename):
        """
        The function creates a valid path for each Project's documentation upload
        and ensures renaming of the file being uploaded if its name is not unique in 
        the selected folder.
        """
        try:
            startup_folder = f'startup_{self.project.startup.pk}'
            project_folder = f'project_{self.project.pk}'

            # Determine the folder path
            folder_path = os.path.join('media', f'startups/{startup_folder}/{project_folder}/')

            # Ensure the folder exists
            os.makedirs(folder_path, exist_ok=True)

            # Replace spaces in the filename with underscores
            filename = filename.replace(" ", "_")
            
            # Create a unique file path
            full_path = os.path.join(folder_path, filename)

            # Check for existing files with the same name and create a unique name
            if os.path.exists(full_path):
                base, extension = os.path.splitext(filename)
                counter = 1
                while os.path.exists(full_path):
                    new_filename = f"{base}_{counter}{extension}"
                    full_path = os.path.join(folder_path, new_filename)
                    counter += 1

            return full_path
        except PermissionError:
            logger.error(f'Permission denied while creating folder or file: {folder_path}')
            raise
        except OSError as e:
            logger.error(f'OS error occurred: {str(e)}')
            raise
        except Exception as e:
            logger.error(f'An unexpected error occurred: {str(e)}')
            raise

    project = models.ForeignKey(Project, on_delete=models.CASCADE, db_index=True,
                                related_name='project_files')
    file_description = models.CharField(max_length=255, blank=False, db_index=True,
                                        verbose_name='file description')
    file = models.FileField(
        upload_to=_generate_upload_path,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Project File'
        verbose_name_plural = 'Project Files'
        ordering = ['project']
    
    def clean(self):
        if not self.file_description.strip():
            raise ValidationError("File description cannot be empty.")


class InvestorProject(models.Model):
    """
    Model represents the relationship between an Investor and a Project,
    including the percentage share the Investor holds in the Project.
    """
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE, db_index=True,
                                 related_name='shortlisted_project')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, db_index=True,
                                related_name='project_share')
    share = models.IntegerField()

    class Meta:
        verbose_name = 'Project Shortlist'
        verbose_name_plural = 'Project Shortlists'
        ordering = ['project', '-share']
        constraints = [
            models.CheckConstraint(
                check=models.Q(share__gte=0) & models.Q(share__lte=100),
                name='percentage_share_range'
            )
        ]

    def __str__(self):
        return (f'Interest of {self.investor} in Project {self.project} '
                f'has changed, current subscription proposal: {self.share}%')

    def clean(self):
        """
        Validates the InvestorProject instance.

        Ensures that the share is within the valid range (0-100).
        """
        if self.share < 0 or self.share > 100:
            raise ValidationError("Share percentage must be between 0 and 100.")

    @classmethod
    def get_total_funding(cls, project_id: int) -> float:
        """
        Calculate the total funding from all investors for a specific project.

        Args:
            project_id (int): The ID of the project.

        Returns:
            float: The total amount of funding.
        """
        try:
            total_funding = cls.objects.filter(
                project_id=project_id).aggregate(total=models.Sum('share'))['total']
            return float(total_funding or 0)
        except Exception as e:
            print(f"An error occurred while calculating total funding: {e}")
        return 0.0
        

class ProjectLog(models.Model):
    """
    Model representing a log entry for project-related events.

    The `ProjectLog` model is used to record significant events related to a Project, 
    such as its creation, updates, or deletion. It captures information about the project 
    at the time of the event, the user who initiated the change, and other contextual data.

    Attributes:
        project (ForeignKey): The related Project instance. It may be null if the project is deleted.
        project_birth_id (int): The original ID of the project when it was first created.
        change_date (DateField): The date when the change was logged.
        change_time (TimeField): The time when the change was logged.
        user_id (int): The ID of the user who performed the action.
        startup_id (int): The ID of the startup associated with the project.
        action (str): A description of the action performed (e.g., 'Created Project',
        'Updated Project', 'Deleted Project').
        previous_state (str): A textual representation of the state before the change.
        modified_state (str): A textual representation of the state after the change.
    """
    project = models.ForeignKey(
        Project, 
        null=True, 
        on_delete=models.SET_NULL, 
        related_name='project_log', 
        db_index=True, 
        verbose_name="Project in DB")
    project_birth_id = models.IntegerField(verbose_name='id')
    change_date = models.DateField(auto_now_add=True, db_index=True)
    change_time = models.TimeField(auto_now_add=True)
    user_id = models.IntegerField(db_index=True)
    startup_id = models.IntegerField(db_index=True)
    action = models.CharField(max_length=50, db_index=True)
    previous_state = models.CharField(max_length=255, verbose_name='Before changes')
    modified_state = models.CharField(max_length=255, verbose_name='After changes')

    class Meta:
        verbose_name = 'Project Log'
        verbose_name_plural = 'Project Logs'
        ordering = ['-pk']

from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from startups.models import Startup
from investors.models import Investor
import os
import logging
from django.utils.text import slugify
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
        duration (float): number of moonths which implementation of the Project is planned for.
        budget_currency (str): currency of the Project's budget
        budget_amount (int): amount of the Project's budget
    """
    name = models.CharField(max_length=150, db_index=True)
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name='projects')
    description = models.CharField(max_length=500, db_index=True)
    # documentation = models.FileField(upload_to=_generate_upload_path, blank=True, null=True)
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
            models.UniqueConstraint(fields=['startup', 'name'],
            name='unique_project_per_startup')
        ]
    
    def save(self, *args, **kwargs):
        """
        Overriding save method to ensure a log is recorded when a Project is created or modified
        """

        # Determine if this is a new object or an existing one
        is_new = self.pk is None

        changes = []
        update_fields = []
        action = 'Created Project' if is_new else 'Update of Project'
        previous_state = 'n/a' if is_new else ''
        modified_state = f'New Project, id: {self.pk}, name: {self.name}' if is_new else ''

        if not is_new:
            try:
                # Fetch the original instance from the database to compare with the current one
                original = Project.objects.get(pk=self.pk)

                # Compare attributes to identify changes
                for field in self._meta.fields:
                    field_name = field.name
                    if getattr(original, field_name) != getattr(self, field_name):
                        changes.append(
                            (field_name, getattr(original, field_name), getattr(self, field_name))
                        )
                        update_fields.append(field_name)

                if changes:
                    # Prepare the previous and modified states
                    previous_state = ', '.join([f'{field}: {old_value}' for field, old_value, _ in changes])
                    modified_state = ', '.join([f'{field}: {new_value}' for field, _, new_value in changes])
                    super().save(update_fields=update_fields, *args, **kwargs)

            except ObjectDoesNotExist:
                logger.error(f"Project with ID {self.pk} does not exist.")
                raise ValidationError(f"Project with ID {self.pk} not found for updating.")
        else:
            super().save(*args, **kwargs)
        
        # Create a new ProjectLog
        ProjectLog.objects.create(
            project=self,
            project_title=self.name,
            change_date=datetime.now().date(),
            change_time=datetime.now().time(),
            user_id=1,  # This is a placeholder
            action=action,
            previous_state=previous_state[:ProjectLog._meta.get_field('previous_state').max_length],
            modified_state=modified_state[:ProjectLog._meta.get_field('modified_state').max_length]
            )
    
    def __str__(self):
        """
        Return the name of the project.
        
        Returns:
            str: The name of the project.
        """
        return self.name

class ProjectFiles(models.Model):

    @staticmethod
    def _generate_upload_path(project, filename):
        '''
        The function creates a valid path for each Project's documentation upload
        and ensures renaming of the file being uploaded if its name is not unique in 
        the selected folder.
        '''
        try:
            # Replace special characters with underscores and truncate to 20 characters
            startup_slug = slugify(project.startup.startup_name)[:20]
            project_slug = slugify(project.name)[:20]

            # Determine the folder path
            folder_path = os.path.join('media', f'projects/{startup_slug}/{project_slug}/')

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


    project = models.ForeignKey(Project, on_delete=models.CASCADE, db_index=True, related_name='project_files')
    file_description = models.CharField(max_length=255, blank=False, db_index=True, verbose_name='file description')
    file = models.FileField(
        upload_to=lambda instance, filename: ProjectFiles._generate_upload_path(instance.project, filename),
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
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE, db_index=True, related_name='shortlisted_project')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, db_index=True, related_name='project_share')
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
        return f'{self.investor} shortlisted Project {self.project}, subscription: {self.share}%'

    def clean(self):
        """
        Validates the InvestorProject instance.

        Ensures that the share is within the valid range (0-100).
        """
        if self.share < 0 or self.share > 100:
            raise ValidationError("Share percentage must be between 0 and 100.")
        
class ProjectLog(models.Model):
    """
    ADD DOCUMENTATION HERE
    """
    project = models.ForeignKey(
        Project, 
        null=True, 
        on_delete=models.SET_NULL, 
        related_name='project_log', 
        db_index=True, 
        verbose_name="Project in DB")
    project_title = models.CharField(max_length=Project._meta.get_field('name').max_length, verbose_name='Project title')
    change_date = models.DateField(auto_now_add=True, db_index=True)
    change_time = models.TimeField(auto_now_add=True)
    user_id = models.IntegerField(db_index=True)
    action = models.CharField(max_length=50, db_index=True)
    previous_state = models.CharField(max_length=255, verbose_name='Before changes')
    modified_state = models.CharField(max_length=255, verbose_name='After changes')

    class Meta:
        verbose_name = 'Project Log'
        verbose_name_plural = 'Project Logs'
        ordering = ['-pk']
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Project, ProjectFiles, ProjectLog
from users.models import UserRoleCompany
from datetime import datetime

def create_log(instance, action, previous_state, modified_state):
    '''
    Creates a log entry for a project action.

    Parameters:
        instance (Project or ProjectFiles): The instance that triggered the log.
        action (str): The action performed.
        previous_state (str): The state before the action.
        modified_state (str): The state after the action.
    '''
    ProjectLog.objects.create(
        project=None if action == 'Deleted Project' else instance,
        project_birth_id=instance.project.pk if action == 'Deleted File of Project' else instance.pk,
        change_date=datetime.now().date(),
        change_time=datetime.now().time(),
        user_id=UserRoleCompany.objects.get(role='startup', company_id=instance.startup_id).user.pk,
        startup_id=instance.startup_id,
        action=action,
        previous_state=previous_state[:255],
        modified_state=modified_state[:255]
    )

def create_file_handling_log(instance, action, previous_state, modified_state):
    '''
    Creates a log entry for a project file action.

    Parameters:
        instance (ProjectFiles): The project file instance that triggered the log.
        action (str): The action performed.
        previous_state (str): The state before the action.
        modified_state (str): The state after the action.
    '''
    ProjectLog.objects.create(
        project=instance.project,
        project_birth_id=instance.project.pk,
        change_date=datetime.now().date(),
        change_time=datetime.now().time(),
        user_id=UserRoleCompany.objects.get(role='startup', company_id=instance.project.startup_id).user.pk,
        startup_id=instance.project.startup_id,
        action=action,
        previous_state=previous_state[:255],
        modified_state=modified_state[:255]
    )


@receiver(post_save, sender=Project)
def create_update_project_log(sender, instance, created, **kwargs):
    '''
    Creates a log entry when a project is created or updated.

    Parameters:
        sender (type): The model class sending the signal.
        instance (Project): The instance of the Project model being saved.
        created (bool): A boolean indicating whether a new record was created.
        **kwargs: Additional keyword arguments.
    '''
    if created:
        action = 'Created Project'
        previous_state = 'n/a'
        modified_state = f'New Project, id: {instance.pk}, name: {instance.name}'
    else:
        action = 'Updated Project'
        changes = getattr(instance, '_changes', [])
        previous_state = ', '.join([f'{field}: {old_value}' for field, old_value, _ in changes])
        modified_state = ', '.join([f'{field}: {new_value}' for field, _, new_value in changes])

    create_log(instance, action, previous_state, modified_state)

@receiver(post_delete, sender=Project)
def delete_project_log(sender, instance, **kwargs):
    '''
    Creates a log entry when a project is deleted.

    Parameters:
        sender (type): The model class sending the signal.
        instance (Project): The instance of the Project model being deleted.
        **kwargs: Additional keyword arguments.
    '''
    create_log(
        instance,
        'Deleted Project',
        f'Project ID: {instance.pk}, Name: {instance.name}', 'n/a'
    )

@receiver(post_save, sender=ProjectFiles)
def create_update_project_file_log(sender, instance, created, **kwargs):
    '''
    Creates a log entry when a project file is created or updated.

    Parameters:
        sender (type): The model class sending the signal.
        instance (ProjectFiles): The instance of the ProjectFiles model being saved.
        created (bool): A boolean indicating whether a new record was created.
        **kwargs: Additional keyword arguments.
    '''
    if created:
        action = 'Added File to Project'
        previous_state = 'n/a'
        modified_state = f'New File, id: {instance.pk}, description: {instance.file_description}'
    else:
        action = 'Updated File Description'
        changes = getattr(instance, '_changes', [])
        previous_state = ', '.join([f'{field}: {old_value}' for field, old_value, _ in changes])
        modified_state = ', '.join([f'{field}: {new_value}' for field, _, new_value in changes])

    create_file_handling_log(instance, action, previous_state, modified_state)

@receiver(post_delete, sender=ProjectFiles)
def delete_project_file_log(sender, instance, **kwargs):
    '''
    Creates a log entry when a project file is deleted.

    Parameters:
        sender (type): The model class sending the signal.
        instance (ProjectFiles): The instance of the ProjectFiles model being deleted.
        **kwargs: Additional keyword arguments.
    '''
    previous_state = f'File ID: {instance.pk}, Description: {instance.file_description}'
    action = 'Deleted File of Project'
    create_file_handling_log(instance, action, previous_state, 'n/a')
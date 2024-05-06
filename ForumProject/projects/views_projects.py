from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.decorators import api_view, permission_classes
from datetime import datetime
from rest_framework.exceptions import NotFound
from .models import Project, ProjectFiles, ProjectLog
from .serializers import ProjectSerializer

from users.permissions import (
    IsInvestorRole,
    IsStartupCompanySelected,
    IsProjectMember,
    IsStartupRole)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for interacting with Project objects.

    Attributes:
        queryset (QuerySet): The queryset of Project objects.
        serializer_class (Serializer): The serializer class for Project objects.
    """
    
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_queryset(self):
        user = self.request.user

        if user.user_info.role == 'investor':
            return Project.objects.all()
        
        startup_id = user.user_info.company_id
        return Project.objects.filter(startup=startup_id)
    
    def get_permissions(self):
        """
        Return the list of permission instances for the current action.

        Depending on the action (e.g., 'list', 'retrieve', 'create', 'update', 'partial_update', 'destroy'),
        different permission classes are applied to control access to the viewset.

        Returns:
            List[BasePermission]: List of permission instances.
        """
        if self.action == 'list':
            permission_classes = [IsInvestorRole | IsStartupRole]
        elif self.action == 'retrieve':
            permission_classes = [IsInvestorRole | IsProjectMember]
        elif self.action == 'create':
            permission_classes = [IsStartupCompanySelected]
        elif self.action == 'update' or self.action == 'partial_update' or self.action == 'destroy':
            permission_classes = [IsStartupCompanySelected, IsProjectMember]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @classmethod
    def create_log(cls, request, event, instance, changes=None, project_file=None):
        '''
        Class method to create a log entry for project-related events.

        This method logs events such as project creation, updates, deletion, or file deletion related to a specific project. 
        It captures the state of the project or file before and after the event, along with additional contextual information.

        Parameters:
            cls (type): The class that defines this method.
            request (HttpRequest): The HTTP request object, used to get user information.
            event (str): The type of event to log. Accepted values are 'new project', 'update project', 'delete project', and 'delete file'.
            instance (Project): The project instance to which the log refers.
            changes (list[tuple[str, any, any]], optional): A list of field changes in the format (field name, old value, new value). Default is None.
            project_file (ProjectFile, optional): A related project file, used if the event is 'delete file'. Default is None.

        Returns:
            None

        Log Creation:
            This method creates a `ProjectLog` object with details about the event, such as the project instance, the user who triggered the event, 
            the action performed, the previous state, and the modified state. The `previous_state` and `modified_state` fields have 
            character length limits, which are enforced to avoid truncation issues.
        
        Event-Specific Information:
            - 'new project': The log records the project creation with a custom message indicating the project ID and name.
            - 'update project': The log captures the list of changed fields with their old and new values.
            - 'delete project': The log records basic project information as the previous state, with no modified state.
            - 'delete file': The log captures the file's ID and description in the previous state, with no modified state.
        
        Note:
            The method uses the current date and time to record when the change occurred. It also fetches the startup ID from 
            the user's associated company information.
        '''

        max_length_previous = ProjectLog._meta.get_field('previous_state').max_length
        max_length_mofified = ProjectLog._meta.get_field('modified_state').max_length

        if event == 'new project':
            action = 'Created Project'
            previous_state='n/a'
            modified_state=f'New Project, id: {instance.pk}, name: {instance.name}'[:max_length_mofified]
        elif event == 'update project':
            action = 'Updated Project'
            previous_state=', '.join([f'{field}: {old_value}' for field, old_value, _ in changes])[:max_length_previous]
            modified_state=', '.join([f'{field}: {new_value}' for field, _, new_value in changes])[:max_length_mofified]
        elif event == 'delete project':
            action = 'Deleted Project'
            previous_state = f'Project ID: {instance.pk}, Name: {instance.name}'[:max_length_previous]
            modified_state = 'n/a'
        elif event == 'delete file':
            action = 'Deleted File of Project'
            previous_state = f'File ID: {project_file.pk}, Description: {project_file.file_description}'[:max_length_previous]
            modified_state = 'n/a'

        ProjectLog.objects.create(
            project = instance,
            project_birth_id = instance.pk,
            change_date = datetime.now().date(),
            change_time = datetime.now().time(),
            user_id = request.user.pk,
            startup_id = request.user.user_info.company_id,
            action = action,
            previous_state = previous_state,
            modified_state = modified_state
        )

    
    def create(self, request, *args, **kwargs):
        """
        Handle project creation and create a log upon success.

        Parameters:
            request (HttpRequest): The HTTP request containing the data for the new Project.
            args: Additional positional arguments.
            kwargs: Additional keyword arguments.

        Returns:
            Response: A response object containing the serialized data of the created Project, 
                    along with HTTP headers for success, if applicable.

        Raises:
            ValidationError: If the input data is invalid.

        Log Creation:
            After successfully creating the Project, this method calls `ProjectViewSet.create_log` to log the 'new project' event, 
            indicating that a new Project has been created. The log contains details like the project ID and name, 
            as well as the user who initiated the request.

        Headers:
            The response includes appropriate headers for successful creation, which can be used by clients to fetch related resources.

        Note:
            - If the input data is invalid, a `ValidationError` is raised, and the response returns a corresponding HTTP status code with error details.
            - The HTTP status code for a successful creation is `HTTP_201_CREATED`.
        """
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        # Save the new project and create a log
        project = serializer.save()

        # create log
        ProjectViewSet.create_log(request, 'new project', project)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        """
        Handle project updates and create a log if there are changes.

        This method handles the update of a Project instance based on the provided request data. 
        If there are changes in the Project's fields, a log entry is created to document these modifications.

        Parameters:
            request (HttpRequest): The HTTP request containing the updated Project data.
            args: Additional positional arguments.
            kwargs: Additional keyword arguments.

        Returns:
            Response: A response object with the serialized data of the updated Project.

        Raises:
            ValidationError: If the input data is invalid.
            Exception: If an unexpected error occurs during the update.

        Log Creation:
            If there are changes to the Project, the method creates a log entry to record the updated fields. 
            The log captures the field names along with their old and new values.

        Error Handling:
            If an exception occurs during the update, a response with a status code `HTTP_500_INTERNAL_SERVER_ERROR` is returned 
            with an appropriate error message.
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True, context={'request': request})
            serializer.is_valid(raise_exception=True)
            
            # Determine changes and create log if needed
            changes = []
            for field_name in Project._meta.fields:
                if getattr(instance, field_name.name) != request.data.get(field_name.name, getattr(instance, field_name.name)):
                    changes.append(
                        (field_name.name, getattr(instance, field_name.name), request.data.get(field_name.name))
                    )

            project = serializer.save()
            
            if changes:
                # create log
                ProjectViewSet.create_log(request, 'update project', project, changes=changes)

            return Response(serializer.data)
        
        except Exception as e:
            return Response(
                {"error": f"An error occurred during update: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, *args, **kwargs):
        '''
        Delete an existing Project along with its associated files and create logs for these actions.

        This method handles the deletion of a Project instance, including its related ProjectFiles. 
        It creates logs for both the project deletion and any associated file deletions.

        Parameters:
            request (HttpRequest): The HTTP request indicating the Project to be deleted.
            args: Additional positional arguments.
            kwargs: Additional keyword arguments.

        Returns:
            Response: A response object with a message indicating successful deletion.

        Raises:
            NotFound: If the Project does not exist.

        Log Creation:
            The method creates log entries for the project deletion and, if applicable, for each ProjectFile deleted during this process.

        Error Handling:
            If the Project does not exist, a `NotFound` exception is raised with an appropriate message.
        '''
        # Get the project instance to be deleted
        project_instance = self.get_object()

        try:
            # Log the project deletion
            ProjectViewSet.create_log(request, 'delete project', project_instance)

            # Find and delete all ProjectFiles related to this project
            project_files = ProjectFiles.objects.filter(project=project_instance)
            
            for project_file in project_files:
                # Log each project file deletion
                ProjectViewSet.create_log(request, 'delete file', project_instance, project_file=project_file)
                # Delete the actual files from the server
                if project_file.file:
                    project_file.file.delete()  # Delete from file system
            
            # Delete all ProjectFiles from the database
            project_files.delete()

            # Now delete the project itself
            self.perform_destroy(project_instance)
        except Project.DoesNotExist:
            raise NotFound("Project not found.")
        
        return Response({"message": "Project and associated files deleted successfully"}, status=status.HTTP_200_OK)

    # Override the default behavior for 'perform_destroy' to use 'destroy' logic
    def perform_destroy(self, instance):
        instance.delete()
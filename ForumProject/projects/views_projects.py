from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.db.models.signals import post_save
from .models import Project, ProjectFiles
from .serializers import ProjectSerializer
from .signals import create_update_project_file_log


from users.permissions import (
    IsInvestorRole,
    IsStartupCompanySelected,
    IsProjectMember,
    IsStartupRole
)


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
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsStartupCompanySelected, IsProjectMember]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

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
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
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
            
            changes = []
            for field in Project._meta.fields:
                field_name = field.name
                old_value = str(getattr(instance, field_name))
                new_value = str(request.data.get(field_name, old_value))
                if old_value != new_value:
                    changes.append((field_name, old_value, new_value))
            
            if changes:
                instance._changes = changes
            
            serializer.save()
            
            return Response(serializer.data)
        
        except Exception as e:
            return Response(
                {"error": f"An error occurred during update: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, *args, **kwargs):
        '''
        Delete an existing Project along with its associated files and ensure only one log entry is created.

        This method handles the deletion of a Project instance, including its related ProjectFiles. 
        It ensures that logs are created for both the project deletion and any associated file deletions
        by marking the project instance with `_log_deletion = True`.

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
            By marking the project instance with `_log_deletion = True`, it ensures that the log entry is created only once.

        Error Handling:
            If the Project does not exist, a `NotFound` exception is raised with an appropriate message.
        '''
        # Get the project instance to be deleted
        project_instance = self.get_object()

        try:
            project_files = ProjectFiles.objects.filter(project=project_instance)

            post_save.disconnect(create_update_project_file_log, sender=ProjectFiles)
            for project_file in project_files:                
                if project_file.file:
                    project_file.file.delete()  # Delete from file system
            
            project_files.delete()
            project_instance.delete()
            post_save.connect(create_update_project_file_log, sender=ProjectFiles)
            return Response({"message": "Project and associated files deleted successfully"}, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
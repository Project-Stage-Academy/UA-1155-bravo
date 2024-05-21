from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
import os
from django.db.models.signals import post_save
from .signals import create_update_project_file_log
from .models import Project, ProjectFiles
from .serializers import ProjectFilesSerializer

from users.permissions import IsProjectMember

class ProjectFilesViewSet(viewsets.ModelViewSet):
    '''
    ViewSet for interacting with ProjectFiles objects.

    This viewset allows CRUD operations for `ProjectFiles`, which are associated with a specific Project.
    It has a default queryset, serializer class, and permission class.

    Attributes:
        queryset (QuerySet): The default queryset for ProjectFiles objects.
        serializer_class (Serializer): The serializer class used to serialize and deserialize ProjectFiles data.
        permission_classes (list): A list of permission classes to determine access control.
    '''
    queryset = ProjectFiles.objects.all()
    serializer_class = ProjectFilesSerializer
    permission_classes = [IsProjectMember]

    def list(self, request, pk=None):
        '''
        List all ProjectFiles associated with a specific Project.

        This method retrieves all `ProjectFiles` for a given Project and checks whether the files exist on the server. 
        If a file is missing, it adds a warning to the `file_description`.

        Parameters:
            request (HttpRequest): The HTTP request object.
            pk (int): The ID of the Project whose files are to be listed.

        Returns:
            Response: An HTTP response containing the serialized list of ProjectFiles.

        Raises:
            Http404: If the Project with the given ID does not exist.

        Note:
            If a file does not exist on the server, the method updates its `file_description` to include a warning.
        '''
        # Get the project with the specified ID
        project_instance = get_object_or_404(Project, id=pk)

        # Get all ProjectFiles related to this project
        queryset = ProjectFiles.objects.filter(project=project_instance)

        # Check if the actual files exist on the server and if not - add warning to file_description 
        for project_file in queryset:
            if project_file.file:
                file_path = project_file.file.path
                if not os.path.exists(file_path):
                    # Add worning and truncate file_description to prevent exceeding max_length
                    file_description = project_file.file_description
                    warning = (f"!!! ATTENTION - THIS FILE IS NOT FOUND - {file_description}")
                    warning = warning[:project_file._meta.get_field("file_description").max_length]
                    # Update file description
                    project_file.file_description = warning
                    project_file.save()
        
        # Serialize the data and return HTTP 200 with the list of ProjectFiles
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, pk=None):
        '''
        Create a new ProjectFiles instance for a specific Project.

        This method creates a new `ProjectFiles` record for the specified Project, based on the request data.
        It requires both a file and a file description to proceed with the creation.

        Parameters:
            request (HttpRequest): The HTTP request containing the file data.
            pk (int): The ID of the Project to which the file will be added.

        Returns:
            Response: An HTTP response containing the serialized created ProjectFiles instance.

        Raises:
            Http404: If the Project with the given ID does not exist.
            serializers.ValidationError: If the file or file description is missing.

        Note:
            The method returns an HTTP 201 status code upon successful creation. If the file or file description 
            is missing, it returns an HTTP 400 status code with an error message.
        '''
        # Ensure the project exists
        project_instance = get_object_or_404(Project, id=pk)

        # Get the file and file description from the request data
        file = request.FILES.get("file")
        file_description = request.data.get("file_description", "").strip()

        if not file or not file_description:
            return Response({"error": "Both file and file description are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new ProjectFiles instance
        project_file = ProjectFiles(
            project=project_instance,
            file=file,
            file_description=file_description
        )
        project_file.save()

        # Serialize and return HTTP 201 with the created ProjectFiles
        serializer = ProjectFilesSerializer(project_file)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # Delete method to remove all ProjectFiles for a specific Project
    def destroy(self, request, pk=None):
        '''
        Delete all ProjectFiles for a specific Project.

        This method deletes all `ProjectFiles` associated with a specific Project, including the corresponding 
        files from the server and their database records.

        Parameters:
            request (HttpRequest): The HTTP request indicating the Project whose files will be deleted.
            pk (int): The ID of the Project whose files are to be deleted.

        Returns:
            Response: An HTTP response indicating successful deletion.

        Raises:
            Http404: If the Project with the given ID does not exist.

        Note:
            This method deletes both the file from the server and the corresponding database record.
            It returns an HTTP 200 status code upon successful deletion.
        '''
        # Ensure the project exists
        project_instance = get_object_or_404(Project, id=pk)

        # Get all ProjectFiles related to this project
        project_files = ProjectFiles.objects.filter(project=project_instance)

        post_save.disconnect(create_update_project_file_log, sender=ProjectFiles)
        # Delete the corresponding files from the server
        for project_file in project_files:
            if project_file.file:
                project_file.file.delete()  # Delete the file from the server
        
        # Delete all ProjectFiles instances from the database
        project_files.delete()
        post_save.connect(create_update_project_file_log, sender=ProjectFiles)

        return Response({"message": "All files deleted successfully"}, status=status.HTTP_200_OK)
    

@api_view(['GET', 'DELETE', 'PUT'])
@permission_classes([IsProjectMember])
def project_file(request, pk, projectfiles_id):
    '''
    Retrieve or delete a specific ProjectFiles instance.

    This function handles two operations based on the HTTP method used in the request: 
    - `GET`: Returns the URL path for the specified file.
    - `DELETE`: Deletes the specified ProjectFiles instance and its associated file from the server.

    Parameters:
        request (HttpRequest): The HTTP request containing the operation (GET or DELETE).
        pk (int): The ID of the Project to which the ProjectFiles belongs.
        projectfiles_id (int): The ID of the specific ProjectFiles instance to retrieve or delete.

    Returns:
        Response: An HTTP response containing the file URL (for GET) or a success message (for DELETE).

    Raises:
        Http404: If the specified ProjectFiles instance or Project does not exist.

    Notes:
        - If the file does not exist when attempting a GET operation, it returns an HTTP 404 status code with an error message.
        - If the DELETE operation is successful, the method returns an HTTP 200 status code with a success message.
    '''
    # Get the ProjectFiles instance to delete
    project_file = get_object_or_404(ProjectFiles, id=projectfiles_id, project_id=pk)
    
    if request.method == 'GET':
        # Return the file URL path
        file_url = project_file.file.url if project_file.file else None
        if file_url:
            return Response({"file_url": file_url}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "File does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
    elif request.method == 'DELETE':
        post_save.disconnect(create_update_project_file_log, sender=ProjectFiles)
        # Delete the file from the server, if it exists
        if project_file.file:
            project_file.file.delete()
        
        # Delete the instance from the database
        project_file.delete()
        post_save.connect(create_update_project_file_log, sender=ProjectFiles)
        
        # Return success response
        return Response({"message": "File deleted successfully"}, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        file_description = request.data.get("file_description", "").strip()
        if not file_description:
            return Response({"error": "File description cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)

        project_file._changes = [
            ('file_description', project_file.file_description, file_description)
        ]
        
        project_file.file_description = file_description
        project_file.save()

        serializer = ProjectFilesSerializer(project_file)
        return Response(serializer.data, status=status.HTTP_200_OK)
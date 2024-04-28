from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.decorators import api_view
import os
from .models import Project, ProjectFiles
from .serializers import ProjectSerializer, ProjectFilesSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for interacting with Project objects.

    Attributes:
        queryset (QuerySet): The queryset of Project objects.
        serializer_class (Serializer): The serializer class for Project objects.
    """
    
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def destroy(self, request, *args, **kwargs):
        # Get the project instance to be deleted
        project_instance = self.get_object()

        # Find and delete all ProjectFiles related to this project
        project_files = ProjectFiles.objects.filter(project=project_instance)
        
        for project_file in project_files:
            # Delete the actual files from the server
            if project_file.file:
                project_file.file.delete()  # Delete from file system
        
        # Delete all ProjectFiles from the database
        project_files.delete()

        # Now delete the project itself
        self.perform_destroy(project_instance)
        
        return Response({"message": "Project and associated files deleted successfully"}, status=status.HTTP_200_OK)

    # Override the default behavior for 'perform_destroy' to use 'destroy' logic
    def perform_destroy(self, instance):
        instance.delete()


class ProjectFilesViewSet(viewsets.ModelViewSet):
    queryset = ProjectFiles.objects.all()
    serializer_class = ProjectFilesSerializer

    def list(self, request, project=None):
        # Get the project with the specified ID
        project_instance = get_object_or_404(Project, id=project)

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

    def create(self, request, project=None):
        # Ensure the project exists
        project_instance = get_object_or_404(Project, id=project)

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
    def destroy(self, request, project=None):
        # Ensure the project exists
        project_instance = get_object_or_404(Project, id=project)

        # Get all ProjectFiles related to this project
        project_files = ProjectFiles.objects.filter(project=project_instance)

        # Delete the corresponding files from the server
        for project_file in project_files:
            if project_file.file:
                project_file.file.delete()  # Delete the file from the server
        
        # Delete all ProjectFiles instances from the database
        project_files.delete()

        return Response({"message": "All files deleted successfully"}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_project_file(request, project, projectfiles_id):
    # Get the ProjectFiles instance to delete
    project_file = get_object_or_404(ProjectFiles, id=projectfiles_id, project_id=project)
    
    # Delete the file from the server, if it exists
    if project_file.file:
        project_file.file.delete()
    
    # Delete the instance from the database
    project_file.delete()
    
    # Return success response
    return Response({"message": "File deleted successfully"}, status=status.HTTP_200_OK)
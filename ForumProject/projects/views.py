from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
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


class ProjectFilesViewSet(viewsets.ModelViewSet):
    queryset = ProjectFiles.objects.all()
    serializer_class = ProjectFilesSerializer

    def list(self, request, project=None):
        # Get the project with the specified ID
        project_instance = get_object_or_404(Project, id=project)

        # Get all ProjectFiles related to this project
        queryset = ProjectFiles.objects.filter(project=project_instance)
        
        # Serialize the data and return HTTP 200 with the list of ProjectFiles
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




    def create(self, request, project=None):
        # Ensure the project exists
        project_instance = get_object_or_404(Project, id=project)

        # Get the file and file description from the request data
        file = request.FILES.get("file")
        file_description = request.data.get("file_description", "").strip()

        if not file:
            return Response({"error": "File is required"}, status=status.HTTP_400_BAD_REQUEST)

        if not file_description:
            return Response({"error": "File description cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new ProjectFiles instance
        project_file = ProjectFiles(
            project=project_instance,
            file=file,
            file_description=file_description,
        )
        project_file.save()

        # Serialize and return HTTP 201 with the created ProjectFiles
        serializer = ProjectFilesSerializer(project_file)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


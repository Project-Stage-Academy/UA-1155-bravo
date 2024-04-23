from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from projects.models import Project
from .models import Startup
from .serializers import StartupSerializer


class StartupViewSet(viewsets.ModelViewSet):
    queryset = Startup.objects.all()
    serializer_class = StartupSerializer

    # Override the destroy method to prevent deletion if startup has open projects
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        projects = Project.objects.filter(startup_id=instance.id)
        
        # Checking whether the startup has open projects
        if any(project.project_status != 'closed' for project in projects):
            raise PermissionDenied("Cannot delete startup with ongoing projects.")
        
        # If the startup has all projects closed, then deletion is possible
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


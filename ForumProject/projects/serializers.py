from rest_framework import serializers

from startups.models import Startup
from .models import Project
from django.core.exceptions import ValidationError


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for the Project model.

    Attributes:
        id (int): The ID of the project (read-only).
        project_name (str): The name of the project.
        project_status (str): The status of the project.
        startup (Startup): The startup associated with the project.
    
    Note: This Serializer is not finished yet. 
    """
    startup = serializers.PrimaryKeyRelatedField(queryset=Startup.objects.all(), allow_null=True)

    class Meta:
        model = Project
        fields = ['id', 'project_name', 'project_status', 'startup']
        read_only_fields = ['id', 'startup']
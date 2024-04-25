from rest_framework import serializers
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
    
    class Meta:
        model = Project
        fields = ['id', 'project_name', 'project_status', 'startup']
        read_only_fields = ['id']  
            
        
    
    def validate_project_name(self, value):
        """
        Validate the uniqueness of the project name for the given startup.

        Parameters:
            value (str): The project name to validate.

        Returns:
            str: The validated project name.

        Raises:
            serializers.ValidationError: If a project with the same name already exists for the startup.
        """
        
        if Project.objects.filter(startup=self.initial_data['startup'], project_name=value).exists():
            raise serializers.ValidationError("A project with this name already exists for the given startup.")
        return value    
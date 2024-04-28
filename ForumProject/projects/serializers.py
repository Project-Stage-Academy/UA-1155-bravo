from rest_framework import serializers
from .models import Project, ProjectFiles, InvestorProject
from django.core.exceptions import ValidationError


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for the Project model.

    Attributes:
        id (int): The ID of the Project (read-only).
        name (str): The name of the Project.
        status (str): The status of the Project.
        startup (Startup): The startup associated with the Project.
        description (str): A description of the Project.
        documentation (files): Files relating to the Project that can be uploaded.
        status (str): The status of the Project, chosen from predefined choices.
        created_at (date-time): date of creation of the Project (read-only).
        updated_at (date-time): date of last modification of the Project (read-only).
        duration (float): number of moonths which implementation of the Project is planned for.
        budget_currency (str): currency of the Project's budget
        budget_amount (int): amount of the Project's budget
    """    
    
    class Meta:
        model = Project
        fields = ['id',
                  'name',
                  'status',
                  'startup',
                  'description',
                  'status',
                  'created_at',
                  'updated_at',
                  'duration',
                  'budget_currency',
                  'budget_amount',
                  'project_share',
                  'project_log'
                 ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'project_share', 'project_log']
            
        
    
    def validate_project_name(self, value):
        """
        Validate the uniqueness of the Pproject name for the given startup.

        Parameters:
            value (str): The Project name to validate.

        Returns:
            str: The validated Project name (with leading white space(s) truncated and first letter capitalized).

        Raises:
            serializers.ValidationError: If a Project with the same name already exists for the Startup.
        """
        
        value = value.strip()
        value = value[0].upper() + value[1:]
        if not value:
            raise serializers.ValidationError("Project name cannot be empty.")
        startup_id = self.initial_data.get('startup')
        if Project.objects.filter(startup_id=startup_id, name=value).exists():
            raise serializers.ValidationError("Project name must be unique for this Startup.")
        return value
    
class ProjectFilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectFiles
        fields = ['id', 'project', 'file_description', 'file']
        read_only_fields = ['id', 'project']

    def validate_file_description(self, value):
        if not value.strip():
            raise serializers.ValidationError("File description cannot be empty.")
        return value
    
class InvestorProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestorProject
        fields = ['id', 'investor', 'project', 'share']
        read_only_fields = ['id', 'investor', 'project', 'share']
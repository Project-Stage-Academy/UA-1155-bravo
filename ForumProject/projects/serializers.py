from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from startups.models import Startup
from .models import Project, ProjectFiles, InvestorProject, ProjectLog
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
    
    startup = serializers.PrimaryKeyRelatedField(read_only=True)
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
        read_only_fields = ['id', 'startup', 'created_at', 'updated_at', 'project_share', 'project_log']
            
    def create(self, validated_data):
        '''
            Create a new Project instance and associate it with a specific Startup.

        This method handles the creation of a new Project instance based on the validated data from the request. 
        It ensures that the user has a selected Startup company, and checks whether the specified Startup exists 
        and belongs to the current user. If all validations pass, it creates and returns a new Project.

        Parameters:
            validated_data (dict): Data validated by the serializer.

        Returns:
            Project: The newly created Project instance.

        Raises:
            serializers.ValidationError: If the user has no associated Startup company, or if the specified Startup does not exist.
        '''
        user = self.context['request'].user
        startup_id = user.user_info.company_id

        if startup_id is None:
            raise serializers.ValidationError("You must select Startup company to create a Project")
        
        try:
            startup = Startup.objects.get(id=startup_id)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(f"Startup with ID {startup_id} does not exist or does not belong to you.")
        validated_data['startup'] = startup
        
        # Create a new project and pass user_id to the save method
        project = Project(**validated_data)
        # project.save(user_id=user.pk)
        project.save()
        return project
    
    def update(self, instance, validated_data):
        '''
        Update an existing Project instance with new validated data.

        This method updates the attributes of an existing Project with the provided validated data 
        and saves the changes to the database.

        Parameters:
            instance (Project): The existing Project instance to be updated.
            validated_data (dict): The validated data with new attribute values.

        Returns:
            Project: The updated Project instance.
        '''
        # Iterate over the validated data and set the corresponding attributes on the instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Save the updated instance
        instance.save()

        return instance
    
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
        startup_id = self.context['request'].user.user_info.company_id
        if Project.objects.filter(startup_id=startup_id, name=value).exists():
            raise serializers.ValidationError("Project name must be unique for this Startup.")
        return value
    
class ProjectFilesSerializer(serializers.ModelSerializer):
    '''
    Serializer for the ProjectFiles model.

    This serializer is used to handle Project-related files, providing validation and serialization logic 
    for the fields associated with Project files.

    Attributes:
        id (int): The unique identifier for the ProjectFile (read-only).
        project (Project): The related Project instance.
        file_description (str): A description for the file.
        file (FileField): The uploaded file.
    '''
    class Meta:
        model = ProjectFiles
        fields = ['id', 'project', 'file_description', 'file']
        read_only_fields = ['id', 'project']

    def validate_file_description(self, value):
        '''
        Validate the description for a Project file to ensure it is not empty.

        This method validates that the file description is not just whitespace 
        and contains meaningful content.

        Parameters:
            value (str): The file description to validate.

        Returns:
            str: The validated file description.

        Raises:
            serializers.ValidationError: If the file description is empty or contains only whitespace.
        '''
        if not value.strip():
            raise serializers.ValidationError("File description cannot be empty.")
        return value
    

class InvestorProjectSerializer(serializers.ModelSerializer):
    '''
    Serializer for the InvestorProject model.

    This serializer is responsible for serializing and deserializing `InvestorProject` instances. 
    It defines the structure for serializing these instances and manages the read-only fields.

    Attributes:
        id (int): The ID of the InvestorProject (read-only).
        investor (User): The investor associated with the project (read-only).
        project (Project): The project associated with the investor (read-only).
        share (float): The share of the project owned by the investor.
    '''
    class Meta:
        model = InvestorProject
        fields = ['id', 'investor', 'project', 'share']
        read_only_fields = ['id', 'investor', 'project', 'share']


class ProjectLogSerializer(serializers.ModelSerializer):
    '''
    Serializer for the ProjectLog model.

    This serializer handles the serialization and deserialization of `ProjectLog` instances. 
    It defines the structure for serializing the project log data and includes read-only fields to prevent modification of logged information.

    Attributes:
        id (int): The ID of the ProjectLog (read-only).
        project (Project): The related Project instance (read-only).
        change_date (date): The date the change was logged (read-only).
        change_time (time): The time the change was logged (read-only).
        user_id (int): The ID of the user who made the change (read-only).
        action (str): The action performed on the project.
        previous_state (str): The previous state of the project or its components.
        modified_state (str): The new or modified state of the project or its components.
    '''
    class Meta:
        model = ProjectLog
        fields = ['id',
                  'project',
                  'change_date',
                  'change_time',
                  'user_id',
                  'action',
                  'previous_state',
                  'modified_state'
                  ]
        read_only_fields = ['id',
                            'project',
                            'change_date',
                            'change_time',
                            'user_id',
                            'action',
                            'previous_state',
                            'modified_state'
                            ]
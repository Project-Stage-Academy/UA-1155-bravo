from rest_framework import serializers
from .models import Project
from django.core.exceptions import ValidationError


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'project_name', 'project_status', 'startup']
        read_only_fields = ['id']  
            
        
    
    def validate_project_name(self, value):
        if Project.objects.filter(startup=self.initial_data['startup'], project_name=value).exists():
            raise serializers.ValidationError("A project with this name already exists for the given startup.")
        return value    
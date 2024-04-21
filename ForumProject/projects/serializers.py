from rest_framework import serializers
from .models import Project
from django.core.exceptions import ValidationError


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'id',
            'project_name',
            'project_status',
            'startup_id',
            
        ]
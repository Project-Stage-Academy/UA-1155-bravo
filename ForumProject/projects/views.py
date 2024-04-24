from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Project
from .serializers import ProjectSerializer

# Create your views here.
class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for interacting with Project objects.

    Attributes:
        queryset (QuerySet): The queryset of Project objects.
        serializer_class (Serializer): The serializer class for Project objects.
    """
    
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


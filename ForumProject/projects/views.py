from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Project
from .serializers import ProjectSerializer

# Create your views here.
class ProjectView(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
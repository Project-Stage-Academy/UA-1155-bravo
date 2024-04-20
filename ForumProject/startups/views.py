from django.shortcuts import render
from rest_framework import viewsets
from .models import Startup
from .serializers import StartupSerializer

class StartupView(viewsets.ModelViewSet):
    queryset = Startup.objects.all()
    serializer_class = StartupSerializer

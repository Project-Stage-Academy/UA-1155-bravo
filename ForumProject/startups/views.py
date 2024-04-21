from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Startup
from .serializers import StartupSerializer

class StartupView(viewsets.ModelViewSet):
    queryset = Startup.objects.all()
    serializer_class = StartupSerializer

    # Override the destroy method to prevent deletion if startup_country starts with "U"
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.startup_country[0].lower() == "u":
            raise PermissionDenied("Cannot delete a startup from country 'U...'.")
        return super().destroy(request, *args, **kwargs)

from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from startups.models import Startup
from users.models import UserRoleCompany
from users.permissions import IsInvestorRole, IsStartupCompanySelected
from .models import Project
from .serializers import ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for interacting with Project objects.

    Attributes:
        queryset (QuerySet): The queryset of Project objects.
        serializer_class (Serializer): The serializer class for Project objects.
    """
    
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsInvestorRole]
        elif self.action == 'retrieve':
            permission_classes = [IsInvestorRole | IsStartupCompanySelected]
        elif self.action == 'create':
            permission_classes = [IsStartupCompanySelected]
        elif self.action == 'update' or self.action == 'partial_update' or self.action == 'destroy':
            permission_classes = [IsStartupCompanySelected]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        user = request.user
        startup_id = user.user_info.company_id
        modified_data = request.data.copy()
        modified_data['startup'] = startup_id
        serializer = self.get_serializer(data=modified_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.user_info.company_id != instance.startup.id:
            return Response({'error': 'You have no permission to update project'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        project = get_object_or_404(self.queryset, pk=kwargs['pk'])
        if request.user.user_info.company_id != project.startup.id and request.user.user_info.role != 'investor':
            return Response({'error': 'You have no permission to view this project'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(project)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.user_info.company_id != instance.startup.id and request.user.user_info.role != 'investor':
            return Response({'error': 'You have no permission to view this project'}, status=status.HTTP_400_BAD_REQUEST)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from startups.models import Startup
from users.models import UserRoleCompany
from users.permissions import IsInvestorRole, IsStartupCompanySelected, IsProjectMember
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
        """
        Return the list of permission instances for the current action.

        Depending on the action (e.g., 'list', 'retrieve', 'create', 'update', 'partial_update', 'destroy'),
        different permission classes are applied to control access to the viewset.

        Returns:
            List[BasePermission]: List of permission instances.
        """
        if self.action == 'list':
            permission_classes = [IsInvestorRole]
        elif self.action == 'retrieve':
            permission_classes = [IsInvestorRole | IsProjectMember]
        elif self.action == 'create':
            permission_classes = [IsStartupCompanySelected]
        elif self.action == 'update' or self.action == 'partial_update' or self.action == 'destroy':
            permission_classes = [IsProjectMember]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """
        Handle create requests to create a new project.

        Args:
            request (Request): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: Response object with serialized data and appropriate status code.
        """
        user = request.user
        startup_id = user.user_info.company_id
        modified_data = request.data.copy()
        modified_data['startup'] = startup_id
        serializer = self.get_serializer(data=modified_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

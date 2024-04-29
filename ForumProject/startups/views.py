from django.shortcuts import render
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from projects.models import Project
from users.permissions import StartupPermission
from .models import Startup
from .serializers import StartupSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import StartupFilter
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination

class StartupViewSet(viewsets.ModelViewSet):
    """
    ViewSet for interacting with Startup objects.

    Attributes:
        queryset (QuerySet): The queryset of Startup objects.
        serializer_class (Serializer): The serializer class for Startup objects.
    """
    
    queryset = Startup.objects.all()
    serializer_class = StartupSerializer
    permission_classes = [StartupPermission,]

    def destroy(self, request, *args, **kwargs):
        """
        The destroy method, which gives access to deletion only if all projects in the startup have the status - closed.

        Parameters:
            request: The request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: A response indicating the result of the deletion.

        Raises:
            PermissionDenied: If the startup has ongoing projects, deletion is not allowed.
        """
        
        instance = self.get_object()
        projects = Project.objects.filter(startup_id=instance.id)
        
        # Checking whether the startup has open projects
        if any(project.status != 'closed' for project in projects):
            raise PermissionDenied("Cannot delete startup with ongoing projects.")
        
        # If the startup has all projects closed, then deletion is possible
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StandardResultsSetPagination(PageNumberPagination):
    """
    A standard pagination class for paginating results.

    Inherits:
        PageNumberPagination: Base class for pagination.

    Attributes:
        page_size (int): The default page size for pagination.
        page_size_query_param (str): The query parameter to specify the page size.
        max_page_size (int): The maximum allowed page size for pagination.

    """    
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    

class StartupList(generics.ListAPIView):
    """
    A view to list all startups with filters.

    Inherits:
        generics.ListAPIView

    Attributes:
        queryset (QuerySet): All startups in the database.
        serializer_class (Serializer): Serializer class for startups.
        filter_backends (list): List of filter backends for the view.
        filterset_class (FilterSet): FilterSet class for startup filtering.
    """   
    queryset = Startup.objects.all()
    serializer_class = StartupSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = StartupFilter
    pagination_class = StandardResultsSetPagination
    
    
class StartupListDetailfilter(generics.ListAPIView):
    """
    A view to search startups.

    Inherits:
        generics.ListAPIView

    Attributes:
        queryset (QuerySet): All startups in the database.
        serializer_class (Serializer): Serializer class for startups.
        filter_backends (list): List of filter backends for the view.
        search_fields (list): List of fields to search against.
    """
    queryset = Startup.objects.all()
    serializer_class = StartupSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['^startup_name', '^startup_industry', '=startup_country']


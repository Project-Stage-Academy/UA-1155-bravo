from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError, NotFound
from projects.models import Project
from users.permissions import IsStartupRole, IsInvestorRole, IsStartupCompanySelected, IsCompanyMember, IsStartupMember
from django.core.exceptions import ValidationError
from .models import Startup
from users.models import UserStartup
from .serializers import StartupSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import StartupFilter
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView

class StartupViewSet(viewsets.ModelViewSet):
    """
    ViewSet for interacting with Startup objects.

    Attributes:
        queryset (QuerySet): The queryset of Startup objects.
        serializer_class (Serializer): The serializer class for Startup objects.
    """
    
    queryset = Startup.objects.all().order_by('id')
    serializer_class = StartupSerializer

    def get_permissions(self):
        """
        Return the list of permission instances for the current action.

        Depending on the action (e.g., 'retrieve', 'create', 'update', 'partial_update', 'destroy'),
        different permission classes are applied to control access to the viewset.

        Returns:
            List[BasePermission]: List of permission instances.
        """
        if self.action == 'retrieve':
            permission_classes = [IsInvestorRole| IsStartupRole, IsStartupMember]
        elif self.action == 'create':
            permission_classes = [IsStartupRole]
        elif self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsStartupRole, IsStartupMember]
        elif self.action == 'destroy':
            permission_classes = [IsStartupRole, IsStartupMember]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_object(self):
        """
        Retrieve and return the startup instance, or raise a 404 error if not found.

        Returns:
            Startup: The startup instance.

        Raises:
            NotFound: If no startup matches the given query.
        """
        queryset = self.filter_queryset(self.get_queryset())
        pk = self.kwargs.get('pk')
        try:
            obj = queryset.get(pk=pk)
        except Startup.DoesNotExist:
            raise NotFound(f"No Startup found for primary key {pk}.")
        self.check_object_permissions(self.request, obj)  # Check object permissions.
        return obj
    
    def create(self, request, *args, **kwargs):
        """
         Handle create requests to create a startup for a user.

         Args:
             request (Request): The HTTP request object.
             *args: Additional positional arguments.
             **kwargs: Additional keyword arguments.

         Returns:
             Response: Response object with serialized data and appropriate status code.

        """
        serializer = StartupSerializer(data=request.data)
        if serializer.is_valid():  
            startup = serializer.save()
            user = request.user
            UserStartup.objects.create(customuser=user, startup=startup, startup_role_id=1) 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Handle requests to update a startup for a user.
        """
        try:
            instance = self.get_object()
        except Startup.DoesNotExist:
            return Response({"error": "Startup not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the user is the owner of the startup
        user_startup = UserStartup.objects.filter(customuser=request.user, startup=instance)
        if not user_startup.exists():
            return Response({"error": "You are not the owner of this startup."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.pop('partial', False))
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            self.perform_update(serializer)
        except Exception as e:
            return Response({"error": f"An error occurred while updating the startup: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.data)


    def destroy(self, request, *args, **kwargs):
        """
        The destroy method, which gives access to deletion only for startups owned by the authenticated user
        and all projects in the startup have the status - closed.
        """
        instance = self.get_object()
        
        # Check if the user is the owner of the startup
        user_startup = UserStartup.objects.filter(customuser=request.user, startup=instance).first()
        if not user_startup:
            raise PermissionDenied("You are not the owner of this startup.")
        
        # Checking whether the startup has open projects using a database query
        if Project.objects.filter(startup_id=instance.id).exclude(status='closed').exists():
            raise PermissionDenied("Cannot delete startup with ongoing projects.")
        
        # If the startup has all projects closed and the user is the owner,
        # then deletion is possible
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
    queryset = Startup.objects.all().order_by('id')
    serializer_class = StartupSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = StartupFilter
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsInvestorRole]

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except AttributeError:
            return Response({"error": "You must log in and select a role"}, status=status.HTTP_403_FORBIDDEN)    
    
    
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





class PersonalStartupList(generics.ListAPIView):
    """
    A view to list startups created by the current user.

    Inherits:
        generics.ListAPIView: Base class for list views.

    Attributes:
        serializer_class (Serializer): Serializer class for startups.
        permission_classes (list): List of permission classes required for the view.

    Methods:
        get_queryset(): Get the queryset of startups created by the current user.

    """
    serializer_class = StartupSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination  

    def get_queryset(self):
        """
        Get the queryset of startups created by the current user.

        Returns:
            QuerySet: Queryset of startups created by the current user.

        """
        user_id = self.request.user.id
        return Startup.objects.filter(userstartup__customuser=user_id)
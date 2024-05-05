from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from projects.models import Project
from users.permissions import IsStartupRole, IsInvestorRole, IsStartupCompanySelected, IsCompanyMember
from rest_framework.permissions import IsAuthenticated

from .models import Startup
from users.models import UserStartup
from .serializers import StartupSerializer
from rest_framework.views import APIView
from users.models import UserStartup
from rest_framework.decorators import action
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
            permission_classes = [IsInvestorRole | IsCompanyMember]
        elif self.action == 'create':
            permission_classes = [IsStartupRole]
        elif self.action == 'update' or self.action == 'partial_update' or self.action == 'destroy':
            permission_classes = [IsCompanyMember]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


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
        if any(project.project_status != 'closed' for project in projects):
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
    queryset = Startup.objects.all().order_by('id')
    serializer_class = StartupSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = StartupFilter
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsInvestorRole]
    
    
    
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


class NotificationPreferencesAPIView(APIView):
    """
    A view to update the notification preferences of the authenticated user's associated startup.

    This view allows authenticated users to update their startup's notification preferences,
    such as email notifications and in-app notifications.

    Methods:
        post(request): Update the notification preferences based on the request data.

    Attributes:
        permission_classes (list): List of permission classes required to access this view.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Update the notification preferences based on the request data.

        This method retrieves the authenticated user and updates their associated startup's
        notification preferences based on the request data.

        Parameters:
            request (Request): The HTTP request object.

        Returns:
            Response: Response object indicating the result of the operation.
        """
        user = request.user

        email_notifications = request.data.get('email_notifications', False)
        in_app_notifications = request.data.get('in_app_notifications', False)

        try:
            startup = Startup.objects.get(customuser=user)
            startup.email_notifications = email_notifications
            startup.in_app_notifications = in_app_notifications
            startup.save()
            return Response({'message': 'Notification preferences updated successfully.'}, status=status.HTTP_200_OK)
        except Startup.DoesNotExist:
            return Response({'error': 'Startup not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

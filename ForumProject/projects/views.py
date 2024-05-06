from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.decorators import api_view, permission_classes
import os
from datetime import datetime
from rest_framework.exceptions import NotFound
from .models import Project, ProjectFiles, InvestorProject, ProjectLog
from investors.models import Investor
from .serializers import ProjectSerializer, ProjectFilesSerializer, InvestorProjectSerializer, ProjectLogSerializer

from startups.models import Startup
from users.models import CustomUser, UserRoleCompany, UserInvestor
from users.permissions import (
    IsInvestorRole,
    IsStartupCompanySelected,
    IsInvestorCompanySelected,
    IsProjectMember, 
    IsCompanyMember, 
    IsStartupRole)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for interacting with Project objects.

    Attributes:
        queryset (QuerySet): The queryset of Project objects.
        serializer_class (Serializer): The serializer class for Project objects.
    """
    
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_queryset(self):
        user = self.request.user

        if user.user_info.role == 'investor':
            return Project.objects.all()
        
        startup_id = user.user_info.company_id
        return Project.objects.filter(startup=startup_id)
    
    def get_permissions(self):
        """
        Return the list of permission instances for the current action.

        Depending on the action (e.g., 'list', 'retrieve', 'create', 'update', 'partial_update', 'destroy'),
        different permission classes are applied to control access to the viewset.

        Returns:
            List[BasePermission]: List of permission instances.
        """
        if self.action == 'list':
            permission_classes = [IsInvestorRole | IsStartupRole]
        elif self.action == 'retrieve':
            permission_classes = [IsInvestorRole | IsProjectMember]
        elif self.action == 'create':
            permission_classes = [IsStartupCompanySelected]
        elif self.action == 'update' or self.action == 'partial_update' or self.action == 'destroy':
            permission_classes = [IsProjectMember]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @classmethod
    def create_log(cls, request, event, instance, changes=None, project_file=None):
        '''
        TODO - add description
        '''

        max_length_previous = ProjectLog._meta.get_field('previous_state').max_length
        max_length_mofified = ProjectLog._meta.get_field('modified_state').max_length

        if event == 'new project':
            action = 'Created Project'
            previous_state='n/a'
            modified_state=f'New Project, id: {instance.pk}, name: {instance.name}'[:max_length_mofified]
        elif event == 'update project':
            action = 'Updated Project'
            previous_state=', '.join([f'{field}: {old_value}' for field, old_value, _ in changes])[:max_length_previous]
            modified_state=', '.join([f'{field}: {new_value}' for field, _, new_value in changes])[:max_length_mofified]
        elif event == 'delete project':
            action = 'Deleted Project'
            previous_state = f'Project ID: {instance.pk}, Name: {instance.name}'[:max_length_previous]
            modified_state = 'n/a'
        elif event == 'delete file':
            action = 'Deleted File of Project'
            previous_state = f'File ID: {project_file.pk}, Description: {project_file.file_description}'[:max_length_previous]
            modified_state = 'n/a'

        print(instance)
        ProjectLog.objects.create(
            project = instance,
            project_birth_id = instance.pk,
            change_date = datetime.now().date(),
            change_time = datetime.now().time(),
            user_id = request.user.pk,
            startup_id = request.user.user_info.company_id,
            action = action,
            previous_state = previous_state,
            modified_state = modified_state
        )

    
    def create(self, request, *args, **kwargs):
        """
        Handle project creation and create a log upon success.
        """
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        # Save the new project and create a log
        project = serializer.save()

        # create log
        ProjectViewSet.create_log(request, 'new project', project)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        """
        Handle project updates and create a log if there are changes.
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True, context={'request': request})
            serializer.is_valid(raise_exception=True)
            
            # Determine changes and create log if needed
            changes = []
            for field_name in Project._meta.fields:
                if getattr(instance, field_name.name) != request.data.get(field_name.name, getattr(instance, field_name.name)):
                    changes.append(
                        (field_name.name, getattr(instance, field_name.name), request.data.get(field_name.name))
                    )

            project = serializer.save()
            
            if changes:
                # create log
                ProjectViewSet.create_log(request, 'update project', project, changes=changes)

            return Response(serializer.data)
        
        except Exception as e:
            return Response(
                {"error": f"An error occurred during update: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, *args, **kwargs):
        # Get the project instance to be deleted
        project_instance = self.get_object()

        try:
            # Log the project deletion
            ProjectViewSet.create_log(request, 'delete project', project_instance)

            # Find and delete all ProjectFiles related to this project
            project_files = ProjectFiles.objects.filter(project=project_instance)
            
            for project_file in project_files:
                # Log each project file deletion
                ProjectViewSet.create_log(request, 'delete file', project_instance, project_file=project_file)
                # Delete the actual files from the server
                if project_file.file:
                    project_file.file.delete()  # Delete from file system
            
            # Delete all ProjectFiles from the database
            project_files.delete()

            # Now delete the project itself
            self.perform_destroy(project_instance)
        except Project.DoesNotExist:
            raise NotFound("Project not found.")
        
        return Response({"message": "Project and associated files deleted successfully"}, status=status.HTTP_200_OK)

    # Override the default behavior for 'perform_destroy' to use 'destroy' logic
    def perform_destroy(self, instance):
        instance.delete()


class ProjectFilesViewSet(viewsets.ModelViewSet):
    queryset = ProjectFiles.objects.all()
    serializer_class = ProjectFilesSerializer
    permission_classes = [IsProjectMember]

    def list(self, request, pk=None):
        # Get the project with the specified ID
        project_instance = get_object_or_404(Project, id=pk)

        # Get all ProjectFiles related to this project
        queryset = ProjectFiles.objects.filter(project=project_instance)

        # Check if the actual files exist on the server and if not - add warning to file_description 
        for project_file in queryset:
            if project_file.file:
                file_path = project_file.file.path
                if not os.path.exists(file_path):
                    # Add worning and truncate file_description to prevent exceeding max_length
                    file_description = project_file.file_description
                    warning = (f"!!! ATTENTION - THIS FILE IS NOT FOUND - {file_description}")
                    warning = warning[:project_file._meta.get_field("file_description").max_length]
                    # Update file description
                    project_file.file_description = warning
                    project_file.save()
        
        # Serialize the data and return HTTP 200 with the list of ProjectFiles
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, pk=None):
        # Ensure the project exists
        project_instance = get_object_or_404(Project, id=pk)

        # Get the file and file description from the request data
        file = request.FILES.get("file")
        file_description = request.data.get("file_description", "").strip()

        if not file or not file_description:
            return Response({"error": "Both file and file description are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new ProjectFiles instance
        project_file = ProjectFiles(
            project=project_instance,
            file=file,
            file_description=file_description
        )
        project_file.save()

        # Serialize and return HTTP 201 with the created ProjectFiles
        serializer = ProjectFilesSerializer(project_file)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # Delete method to remove all ProjectFiles for a specific Project
    def destroy(self, request, pk=None):
        # Ensure the project exists
        project_instance = get_object_or_404(Project, id=pk)

        # Get all ProjectFiles related to this project
        project_files = ProjectFiles.objects.filter(project=project_instance)

        # Delete the corresponding files from the server
        for project_file in project_files:
            if project_file.file:
                project_file.file.delete()  # Delete the file from the server
        
        # Delete all ProjectFiles instances from the database
        project_files.delete()

        return Response({"message": "All files deleted successfully"}, status=status.HTTP_200_OK)


@api_view(['GET', 'DELETE'])
@permission_classes([IsProjectMember])
def project_file(request, pk, projectfiles_id):
    # Get the ProjectFiles instance to delete
    project_file = get_object_or_404(ProjectFiles, id=projectfiles_id, project_id=pk)
    
    if request.method == 'GET':
        # Return the file URL path
        file_url = project_file.file.url if project_file.file else None
        if file_url:
            return Response({"file_url": file_url}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "File does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
    elif request.method == 'DELETE':
        # Delete the file from the server, if it exists
        if project_file.file:
            project_file.file.delete()
        
        # Delete the instance from the database
        project_file.delete()
        
        # Return success response
        return Response({"message": "File deleted successfully"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsInvestorRole, IsCompanyMember])
def follow(request, project_id):
    """
    Shortlist a project for an investor with a share of zero.
    """
    
    investor_id = request.user.user_info.company_id

    # Check if an InvestorProject with the given project_id and investor_id already exists
    if InvestorProject.objects.filter(project_id=project_id, investor_id=investor_id).exists():
        return Response({"error": "Project is already followed by this investor"},
                        status=status.HTTP_400_BAD_REQUEST)
    
    # Create a new InvestorProject with share=0
    investor_project = InvestorProject(
        project_id=project_id,
        investor_id=investor_id,
        share=0
    )
    investor_project.save()

    return Response({"message": "Project shortlisted with zero share"}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsInvestorRole, IsCompanyMember])
def subscription(request, project_id, share):
    """
    Subscribe an investor to a project with a given share.
    If a record already exists, update the share value.
    """

    if share < 0 or share > 100:
        return Response(
            {"error": "Share must be greater between zero and 100"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    investor_id = request.user.user_info.company_id

    # Check if an InvestorProject with the given project_id and investor_id already exists
    try:
        investor_project = InvestorProject.objects.get(project_id=project_id, investor_id=investor_id)
        
        investor_project.share = share
        investor_project.save()

        return Response(
            {"message": f"Project share updated to {share}."}, status=status.HTTP_200_OK)

    # If no record exists, create a new one
    except InvestorProject.DoesNotExist:
        investor_project = InvestorProject(
            project_id=project_id,
            investor_id=investor_id,
            share=share
        )
        investor_project.save()

        return Response(
            {"message": f"Project subscribed with share {share}."},
            status=status.HTTP_201_CREATED
        )

@api_view(['POST'])
@permission_classes([IsInvestorRole, IsCompanyMember])
def delist_project(request, project_id):
    """
    Delist a project for a specific investor.
    """
    investor_id = request.user.user_info.company_id
    investor_project = get_object_or_404(InvestorProject, project_id=project_id, investor_id=investor_id)
    investor_project.delete()

    return Response({"message": "Project delisted for the investor"}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsCompanyMember])
def view_followed_projects(request):
    """
    TODO description
    """
    
    user = request.user
    if user.user_info.role == 'investor':
        # Filter any Project(s) that the Investor follows
        followed_projects = InvestorProject.objects.filter(investor__id=user.user_info.company_id)
    else:
        # Find projects created by the startup and followed by an investor
        startup_id = user.user_info.company_id
        followed_projects = InvestorProject.objects.filter(project__startup=startup_id)

    # Serialize the data and return the list
    serializer = InvestorProjectSerializer(followed_projects, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsStartupRole])
def view_logs(request, pk):
    startup_id = request.user.user_info.company_id
    project_logs = ProjectLog.objects.filter(project_birth_id=pk, startup_id=startup_id)

    if not project_logs:
        return Response(
            {"error": "Project was not created or does not belong to you"},
            status=status.HTTP_400_BAD_REQUEST
            )
    serializer = ProjectLogSerializer(project_logs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
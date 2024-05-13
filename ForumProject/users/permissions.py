from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission
from .models import UserStartup
from projects.models import Project
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied


class IsRoleSelected(BasePermission):
    """
    Permission class to check if the authenticated user has a specific role.

    Attributes:
        ROLE (str): The role to check for. Must be defined in subclasses.
    """
    ROLE = None

    def has_permission(self, request, view):
        """
        Check if the authenticated user has the specified role.

        Args:
            request: The request object.
            view: The view object.

        Returns:
            bool: True if the user has the specified role, False otherwise.
        """
        if request.user.user_info.role != self.ROLE:
            return False
        return True


class IsStartupRole(IsRoleSelected):
    """
    Permission class to check if the authenticated user has the role of a startup.
    """
    ROLE = 'startup'
    
    def has_permission(self, request, view):
        """
        Check if the user is logged in and has the role of a startup.

        Args:
            request: The request object.
            view: The view object.

        Returns:
            bool: True if the user is logged in and has the role of a startup, False otherwise.
                
        Raises:
            PermissionDenied: If the user is not logged in or does not have the role of a startup.
        """
        if not request.user.is_authenticated or not hasattr(request.user, 'user_info'):
            raise PermissionDenied({"error": "Please log in to access this resource."})
        return request.user.user_info.role == 'startup'


class IsInvestorRole(IsRoleSelected):
    """
    Permission class to check if the authenticated user has the role of an investor.
    """
    ROLE = 'investor'

    def has_permission(self, request, view):
        """
        Check if the user is logged in and has the role of an investor.

        Args:
            request: The request object.
            view: The view object.

        Returns:
            bool: True if the user is logged in and has the role of an investor, False otherwise.

        Raises:
            PermissionDenied: If the user is not logged in or does not have the role of an investor.
        """
        if not request.user.is_authenticated:
            raise PermissionDenied({"error": "Please log in to access this resource."})

        if hasattr(request.user, 'user_info') and request.user.user_info.role == 'investor':
            return True
        else:
            return False

class IsCompanySelected(BasePermission):
    """
    Permission class to check if the authenticated user has selected a company.

    Attributes:
        ROLE (str): The role to check for. Must be defined in subclasses.
    """
    ROLE = None

    def has_permission(self, request, view):
        """
        Check if the authenticated user has selected a company of the specified role.

        Args:
            request: The request object.
            view: The view object.

        Returns:
            bool: True if the user has selected a company of the specified role, False otherwise.
        """
        if request.user.user_info.company_id != 0 and request.user.user_info.role == self.ROLE:
            return True
        return False


class IsStartupCompanySelected(IsCompanySelected):
    """
    Permission class to check if the authenticated user, with the role of a startup,
    has selected a company.
    """
    ROLE = 'startup'


class IsInvestorCompanySelected(IsCompanySelected):
    """
    Permission class to check if the authenticated user, with the role of an investor,
    has selected a company.
    """
    ROLE = 'investor'


class IsRole(BasePermission):
    """
    Permission class to check if the authenticated user has a valid role.

    A valid role is either 'startup' or 'investor'.
    """
    def has_permission(self, request, view):
        """
        Check if the authenticated user has a valid role.

        Args:
            request: The request object.
            view: The view object.

        Returns:
            bool: True if the user has a valid role, False otherwise.
        """
        if request.user.user_info.role not in ['startup', 'investor']:
            return False
        return True


class IsCompanyMember(BasePermission):
    """
    Permission class to check if the authenticated user is a member of a specified company.

    The user is considered a member if their company_id matches the company's primary key (pk).
    """
    def has_permission(self, request, view):
        """
        Check if the authenticated user is a member of the specified company.

        Args:
            request: The request object.
            view: The view object.

        Returns:
            bool: True if the user is a member of the specified company, False otherwise.
        """
        try:
            return request.user.user_info.company_id == view.kwargs['pk']
        except AttributeError:
            return False


class IsProjectMember(BasePermission):
    """
    Permission class to check if the authenticated user is a member of
    the startup associated with a project.

    The user is considered a member if their company_id matches
    the ID of the startup associated with the project.
    """
    def has_permission(self, request, view):
        """
        Check if the authenticated user is a member of the startup associated with the project.

        Args:
            request: The request object.
            view: The view object.

        Returns:
            bool: True if the user is a member of the startup associated with the project,
                  False otherwise.
        """
        try:
            project = get_object_or_404(Project, pk=view.kwargs['pk'])
            return request.user.user_info.company_id == project.startup.id
        except AttributeError:
            return False


class IsStartupMember(BasePermission):
    """
    Permission class to check if the authenticated user is a member of a startup.
    """
    ROLE = 'startup'

    def has_permission(self, request, view):
        """
        Check if the authenticated user is a member of a startup.

        Args:
            request: The request object.
            view: The view object.

        Returns:
            bool: True if the user is a member of a startup, False otherwise.
        """     
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return False

        # Check if there is a UserStartup entry matching the user and startup
        user_startup = UserStartup.objects.filter(customuser=request.user, startup=view.get_object()).exists()
        
        return user_startup
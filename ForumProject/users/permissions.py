from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission

from projects.models import Project


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


class IsInvestorRole(IsRoleSelected):
    """
    Permission class to check if the authenticated user has the role of an investor.
    """
    ROLE = 'investor'


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
    Permission class to check if the authenticated user, with the role of a startup, has selected a company.
    """
    ROLE = 'startup'


class IsInvestorCompanySelected(IsCompanySelected):
    """
    Permission class to check if the authenticated user, with the role of an investor, has selected a company.
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
    Permission class to check if the authenticated user is a member of the startup associated with a project.

    The user is considered a member if their company_id matches the ID of the startup associated with the project.
    """
    def has_permission(self, request, view):
        """
        Check if the authenticated user is a member of the startup associated with the project.

        Args:
            request: The request object.
            view: The view object.

        Returns:
            bool: True if the user is a member of the startup associated with the project, False otherwise.
        """
        try:
            project = get_object_or_404(Project, pk=view.kwargs['pk'])
            return request.user.user_info.company_id == project.startup.id
        except AttributeError:
            return False

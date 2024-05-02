from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission

from projects.models import Project


class IsRoleSelected(BasePermission):
    ROLE = None

    def has_permission(self, request, view):
        if request.user.user_info.role != self.ROLE:
            return False
        return True


class IsStartupRole(IsRoleSelected):
    ROLE = 'startup'


class IsInvestorRole(IsRoleSelected):
    ROLE = 'investor'


class IsCompanySelected(BasePermission):
    ROLE = None

    def has_permission(self, request, view):
        if request.user.user_info.company_id != 0 and request.user.user_info.role == self.ROLE:
            return True
        return False


class IsStartupCompanySelected(IsCompanySelected):
    ROLE = 'startup'


class IsInvestorCompanySelected(IsCompanySelected):
    ROLE = 'investor'


class IsRole(BasePermission):
    def has_permission(self, request, view):
        if request.user.user_info.role not in ['startup', 'investor']:
            return False
        return True


class IsCompanyMember(BasePermission):
    def has_permission(self, request, view):
        try:
            return request.user.user_info.company_id == view.kwargs['pk']
        except AttributeError:
            return False


class IsProjectMember(BasePermission):
    def has_permission(self, request, view):
        try:
            project = get_object_or_404(Project, pk=view.kwargs['pk'])
            return request.user.user_info.company_id == project.startup.id
        except AttributeError:
            return False

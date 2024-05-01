from django.db.models import Q
from rest_framework.permissions import BasePermission

from projects.models import InvestorProject
from .models import UserStartup, UserInvestor


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


class AnyPermission(BasePermission):
    def __init__(self, *perms):
        self.perms = perms

    def has_permission(self, request, view):
        return any(perm().has_permission(request, view) for perm in self.perms)

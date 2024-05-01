from rest_framework.permissions import BasePermission


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

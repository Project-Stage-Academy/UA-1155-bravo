from django.db.models import Q
from rest_framework.permissions import BasePermission

from projects.models import InvestorProject
from .models import UserStartup, UserInvestor


class StartupPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if view.action == 'list':
            return UserInvestor.objects.filter(customuser=request.user.id).exists()
        elif view.action == 'create':
            return True
        elif view.action == 'retrieve':
            return True
        elif view.action in ['update', 'partial_update', 'destroy']:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if view.action == 'retrieve':
            return (UserInvestor.objects.filter(customuser=request.user.id).exists() or
                    UserStartup.objects.filter(Q(customuser=request.user.id) & Q(startup=obj.id)).exists())
        elif view.action in ['update', 'partial_update', 'destroy']:
            return UserStartup.objects.filter(Q(customuser=request.user.id) & Q(startup=obj.id)).exists()
        else:
            return False


class InvestorPermission(BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if view.action == 'list':
            return False  # update due to followers(?)
        elif view.action == 'create':
            return True
        elif view.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        # a retrieve permission will be updated after implementing follows for startups
        if view.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return UserInvestor.objects.filter(Q(customuser=request.user.id) & Q(investor=obj.id)).exists()
        else:
            return False


class ProjectPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if view.action == 'list':
            return UserInvestor.objects.filter(customuser=request.user.id).exists()
        elif view.action == 'create':  # need updates
            return UserStartup.objects.filter(customuser=request.user.id).exists()
        elif view.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if view.action == 'retrieve':
            return (InvestorProject.objects.filter(Q(investor=request.user.id) & Q(project=obj.id)).exists() or
                    UserStartup.objects.filter(Q(customuser=request.user.id) & Q(startup=obj.startup.id)).exists())
        elif view.action in ['update', 'partial_update', 'destroy']:
            return UserStartup.objects.filter(Q(customuser=request.user.id) & Q(startup=obj.startup.id)).exists()
        else:
            return False
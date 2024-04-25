from django.db.models import Q
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import UserStartup, UserInvestor


class JWTStatus:
    def define_status(self, request):
        auth = JWTAuthentication()
        try:
            user, token = auth.authenticate(request)
        except Exception as e:
            return False

        if user and token:
            payload = token.payload
            return payload['status']


class StartupPermission(BasePermission):
    def has_permission(self, request, view):
        auth = JWTAuthentication()
        try:
            user, token = auth.authenticate(request)
        except Exception as e:
            return False

        status = None
        if user and token:
            payload = token.payload
            status = payload['status']

        if view.action == 'list':
            return UserInvestor.objects.filter(customuser=request.user.id).exists() and status == 'investor'
        elif view.action == 'create':
            return UserStartup.objects.filter(customuser=request.user.id).exists() and status == 'startup'
        elif view.action == 'retrieve':
            return True
        elif view.action in ['update', 'partial_update', 'destroy']:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        auth = JWTAuthentication()
        try:
            user, token = auth.authenticate(request)
        except Exception as e:
            return False

        status = None
        if user and token:
            payload = token.payload
            status = payload['status']

        if view.action == 'retrieve':
            return (UserInvestor.objects.filter(customuser=request.user.id).exists() or
                    UserStartup.objects.filter(Q(customuser=request.user.id) & Q(startup=obj.id)).exists())
        elif view.action in ['update', 'partial_update', 'destroy']:
            return UserStartup.objects.filter(
                Q(customuser=request.user.id) & Q(startup=obj.id)).exists() and status == 'startup'
        else:
            return False


class InvestorPermission(BasePermission):

    def has_permission(self, request, view):
        if view.action == 'list':
            return False
        elif view.action == 'create':
            return UserInvestor.objects.filter(customuser=request.user.id).exists()
        elif view.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return UserInvestor.objects.filter(customuser=request.user.id).exists()
        else:
            return False

    def has_object_permission(self, request, view, obj):
        # a retrieve permission will be updated after implementing follows for startups
        if view.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return UserInvestor.objects.filter(Q(customuser=request.user.id) & Q(investor=obj.id)).exists()
        else:
            return False

from rest_framework import generics, viewsets, status
from users.permissions import IsInvestorRole
from notifications.models import Notification, StartupNotificationPrefs, InvestorNotificationPrefs
from notifications.serializers import (
    NotificationSerializer, 
    StartupNotificationPrefsSerializer, 
    InvestorNotificationPrefsSerializer
)
from users.permissions import IsStartupCompanySelected, IsInvestorCompanySelected
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.db import IntegrityError
from django.core.exceptions import ValidationError

class NotificationListView(generics.ListAPIView):
    """
    View for listing notifications of the authenticated user.

    Serializer class: NotificationSerializer
    Permission classes: IsInvestorRole
    """

    serializer_class = NotificationSerializer
    permission_classes = [IsInvestorRole]

    def get_queryset(self):
        """
        Get the queryset of notifications for the authenticated user.

        Returns:
            Queryset: Notifications filtered by the ID of the current authenticated user.
        """
        # Get the ID of the current authenticated user
        user_id = self.request.user.id
        
        # Filter notifications by the ID of the investor matching the ID of the current user
        return Notification.objects.filter(investor__userinvestor__customuser_id=user_id)
    

class NotificationPrefsViewSet(viewsets.ModelViewSet):
    """
    TODO
    """
    permission_classes = [IsStartupCompanySelected | IsInvestorCompanySelected]

    def get_queryset(self):
        """
        TODO
        """
        user_role = self.request.user.user_info.role
        if user_role == 'investor':
            return InvestorNotificationPrefs.objects.all()
        return StartupNotificationPrefs.objects.all()
    
    def get_serializer_class(self):
        """
        TODO
        """
        user_role = self.request.user.user_info.role
        if user_role == 'investor':
            return InvestorNotificationPrefsSerializer
        return StartupNotificationPrefsSerializer
    

    def retrieve(self, request, *args, **kwargs):
        """
        TODO
        """
        user_role =  request.user.user_info.role.capitalize()
        company_id = request.user.user_info.company_id
        if not company_id:
            return Response(f'Notifications Preferences are specific to each {user_role}. Please first select {user_role}',
                            status=status.HTTP_400_BAD_REQUEST)


        if user_role == 'Investor':
            try:
                preferences = InvestorNotificationPrefs.objects.get(investor_id=company_id)
            except InvestorNotificationPrefs.DoesNotExist:
                raise NotFound("Preferences for this Investor were not found.")
            serializer = self.get_serializer(preferences, context={'investor_id': company_id})
        else: 
            try:
                preferences = StartupNotificationPrefs.objects.get(startup_id=company_id)
            except StartupNotificationPrefs.DoesNotExist:
                raise NotFound("Preferences for this Startup were not found.")
            
            serializer = self.get_serializer(preferences, context={'startup_id': company_id})
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """
        TODO
        """
        user_role =  request.user.user_info.role.capitalize()
        company_id = request.user.user_info.company_id
        if not company_id:
            return Response(f"Please first select {user_role} to set notifications preferences for it.", status=status.HTTP_400_BAD_REQUEST)

        if user_role == 'Investor':
            try:
                instance = InvestorNotificationPrefs.objects.get(investor_id=company_id)
            except InvestorNotificationPrefs.DoesNotExist:
                return Response("Preferences for this Investor were not found.", status=status.HTTP_400_BAD_REQUEST)
            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(instance, data=request.data, partial=partial, context={'investor_id': company_id})
        else:
            try:
                instance = StartupNotificationPrefs.objects.get(startup_id=company_id)
            except StartupNotificationPrefs.DoesNotExist:
                return Response("Preferences for this Startup were not found.", status=status.HTTP_400_BAD_REQUEST)
            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(instance, data=request.data, partial=partial, context={'startup_id': company_id})
        
        try:
            serializer.is_valid(raise_exception=True)
            for key in request.data.keys():
                if key not in serializer.fields or not isinstance(request.data[key], bool):
                    raise ValidationError(f"At least one field ('{key}') is not a valid boolean field.")
            serializer.save()
        except IntegrityError:
            return Response("Integrity Error: Could not save preferences.", status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response(f"Validation Error: {str(e)}", status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data)
from rest_framework import generics, viewsets, status
from users.permissions import IsInvestorRole
from notifications.models import Notification, NotificationPreferences
from notifications.serializers import NotificationSerializer, NotificationPreferencesSerializer
from users.permissions import IsStartupCompanySelected
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
    

class NotificationsPreferencesViewSet(viewsets.ModelViewSet):
    """
    TODO
    """
    # queryset = NotificationPreferences
    queryset = NotificationPreferences.objects.all()
    serializer_class = NotificationPreferencesSerializer
    permission_classes = [IsStartupCompanySelected]

    def retrieve(self, request, *args, **kwargs):
        """
        TODO
        """
        startup_id = request.user.user_info.company_id
        if not startup_id:
            return Response('Notifications Preferences are specific to each Startup. Please first select a Startup',
                            status=status.HTTP_404_NOT_FOUND)


        try:
            preferences = NotificationPreferences.objects.get(startup_id=startup_id)
        except NotificationPreferences.DoesNotExist:
            raise NotFound("Preferences for this startup were not found.")
        
        serializer = self.get_serializer(preferences)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """
        TODO
        """
        startup_id = request.user.user_info.company_id
        if not startup_id:
            return Response("Please first select Startup to set notifications preferences for it.", status=status.HTTP_404_NOT_FOUND)
        try:
            instance = NotificationPreferences.objects.get(startup_id=startup_id)
        except NotificationPreferences.DoesNotExist:
            return Response("Preferences for this startup were not found.", status=status.HTTP_404_NOT_FOUND)
        
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except IntegrityError:
            return Response("Integrity Error: Could not save preferences.", status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response(f"Validation Error: {str(e)}", status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data)
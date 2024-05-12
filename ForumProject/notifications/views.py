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
    Viewset for managing notification preferences of a startup.

    Retrieves and updates notification preferences associated with the authenticated startup.
    """
    # queryset = NotificationPreferences
    queryset = NotificationPreferences.objects.all()
    serializer_class = NotificationPreferencesSerializer
    permission_classes = [IsStartupCompanySelected]

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves notification preferences for the authenticated startup.

        Retrieves the notification preferences associated with the authenticated startup based on the 
        startup ID from the request. If preferences are not found for the startup, a 404 error response is 
        returned.

        Args:
        - request (Request): The incoming GET request.
        - args: Additional arguments.
        - kwargs: Additional keyword arguments.

        Returns:
        - Response: Response containing the retrieved notification preferences or a 404 error if preferences 
        are not found for the startup.
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
        Updates notification preferences for the authenticated startup.

        If any of the fields are not boolean or are not listed in the model `NotificationPreferences`, 
        a 400 error response is returned. It is okay if only some of the fields from `NotificationPreferences` 
        are included in the body of the PUT request (in which case the values of fields not included 
        should not be amended).

        Args:
        - request (Request): The incoming PUT request.
        - args: Additional arguments.
        - kwargs: Additional keyword arguments.

        Returns:
        - Response: Response indicating success or failure of the update operation.
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
            for key in request.data.keys():
                if key not in serializer.fields or not isinstance(request.data[key], bool):
                    raise ValidationError(f"At leasst one field ('{key}') is not a valid boolean field.")
            serializer.save()
        except IntegrityError:
            return Response("Integrity Error: Could not save preferences.", status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response(f"Validation Error: {str(e)}", status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data)
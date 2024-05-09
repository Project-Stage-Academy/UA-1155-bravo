from rest_framework import generics
from users.permissions import IsInvestorRole
from notifications.models import Notification
from notifications.serializers import NotificationSerializer

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

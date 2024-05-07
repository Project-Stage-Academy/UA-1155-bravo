from rest_framework import generics
from .models import NotificationPreference
from .serializers import NotificationPreferenceSerializer
from rest_framework.permissions import IsAuthenticated

class NotificationPreferenceAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return NotificationPreference.objects.get_or_create(user=self.request.user)[0]
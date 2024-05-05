from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Startup


class NotificationPreferencesAPIView(APIView):
    def post(self, request):
        user = request.user  # Assuming user authentication is implemented
        # Assuming request data is in JSON format with keys 'email_notifications' and 'in_app_notifications'
        email_notifications = request.data.get('email_notifications', False)
        in_app_notifications = request.data.get('in_app_notifications', False)

        try:
            startup = Startup.objects.get(user=user)  # Assuming Startup model has a ForeignKey to User model
            startup.email_notifications = email_notifications
            startup.in_app_notifications = in_app_notifications
            startup.save()
            return Response({'message': 'Notification preferences updated successfully.'}, status=status.HTTP_200_OK)
        except Startup.DoesNotExist:
            return Response({'error': 'Startup not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


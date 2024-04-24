import jwt
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (TokenObtainPairView as BaseTokenObtainPairView,
                                            TokenRefreshView as BaseTokenRefreshView)

from .models import CustomUser
from .serializers import UserRegisterSerializer, RecoveryEmailSerializer, PasswordResetSerializer
from .utils import Util


class TokenObtainPairView(BaseTokenObtainPairView):
    throttle_scope = 'token_obtain'


class TokenRefreshView(BaseTokenRefreshView):
    throttle_scope = 'token_refresh'


class UserRegistrationView(APIView):
    """
       A view for user registration.

       This view handles POST requests for user registration.
       It receives user registration data, validates it, creates a new user if valid,
       generates an authentication token, and sends a confirmation email to the user.

       Attributes:
       - permission_classes: The list of permission classes applied to this view.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle POST requests for user registration.

        Parameters:
        - request: The request object containing user registration data.

        Returns:
        - A Response object with the result of the user registration.
            - If the registration data is valid, a new user is created, an authentication token
            is generated, and a confirmation email is sent. Returns the serialized user data
            with HTTP status code 201 (Created).
            - If the registration data is invalid, returns the validation errors with
            HTTP status code 400 (Bad Request).
        """
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            new_user = serializer.save()
            token = RefreshToken.for_user(new_user).access_token
            Util.send_email(get_current_site(request).domain, new_user, token)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    """
    A view for verifying user email activation tokens.

    This view handles GET requests with an activation token in the URL.
    If the token is valid and not expired, it activates the user associated with the token.

    Attributes:
    - permission_classes: The list of permission classes applied to this view.
    """
    permission_classes = [AllowAny]

    def post(self, request, token):
        """
        Handle GET requests to verify email activation.

        Parameters:
        - request: The request object.
        - token: The activation token extracted from the URL.

        Returns:
        - A Response object with the result of the email verification.
            - If the token is valid and the associated user is successfully activated,
            returns a success message with HTTP status code 200.
            - If the token is expired, returns an error message indicating the activation has expired
            with HTTP status code 400.
            - If the token is invalid, returns an error message indicating an invalid token
            with HTTP status code 400.
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, settings.SIMPLE_JWT['ALGORITHM'])
            user = CustomUser.objects.get(id=payload['user_id'])
            if not user.is_active:
                user.is_active = True
                user.save()
            return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class PasswordRecoveryView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')

        serializer = RecoveryEmailSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = CustomUser.objects.get(email=email)
                token = RefreshToken.for_user(user).access_token
                Util.send_recovery_email(get_current_site(request).domain, user, token)
                return Response({'success': 'Email was sent successfully'}, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        return Response({'success': 'Enter new data'}, status=status.HTTP_200_OK)

    def post(self, request, token):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, settings.SIMPLE_JWT['ALGORITHM'])
                user = CustomUser.objects.get(id=payload['user_id'])
                user.set_password(serializer.validated_data.get('password'))
                user.save()
                return Response({'success': 'Password has been successfully updated'}, status=status.HTTP_200_OK)
            except jwt.ExpiredSignatureError as identifier:
                return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
            except jwt.exceptions.DecodeError as identifier:
                return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

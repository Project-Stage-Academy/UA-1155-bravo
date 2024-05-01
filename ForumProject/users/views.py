import jwt
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (TokenObtainPairView as BaseTokenObtainPairView,
                                            TokenRefreshView as BaseTokenRefreshView)
from django.http import JsonResponse

from investors.models import Investor
from investors.serializers import InvestorSerializer
from startups.models import Startup
from startups.serializers import StartupSerializer
from .models import CustomUser, UserRoleCompany, UserStartup, UserInvestor
from .serializers import UserRegisterSerializer, RecoveryEmailSerializer, PasswordResetSerializer, RoleSerializer, \
    CompanySerializer
from .utils import Util


class TokenObtainPairView(BaseTokenObtainPairView):
    throttle_scope = 'token_obtain'

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        token = response.data.get('access')

        if token:
            # Set the token in a cookie with appropriate settings
            response.set_cookie(
                'jwt_token',
                token,
                max_age=300,  # Token lifetime (5 minutes)
                httponly=True,  # To prevent JavaScript access
                secure=True,  # If using HTTPS
                samesite='Strict',
                # helps prevent Cross-Site Request Forgery (CSRF) attacks and reduces the risk of unauthorized cross-site data exchange
            )

        return response


class TokenRefreshView(BaseTokenRefreshView):
    throttle_scope = 'token_refresh'

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        # Get the refreshed token from the response data
        token = response.data.get('access')

        if token:
            response.set_cookie(
                'jwt_token',
                token,
                max_age=300,
                httponly=True,
                secure=True,
                samesite='Strict',
            )

        return response


class RoleSelectionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if UserRoleCompany.objects.filter(user=user).exists():
                user_role = UserRoleCompany.objects.get(user=user)
                user_role.role = serializer.validated_data['role']
                user_role.save()
            else:
                UserRoleCompany.objects.create(user=user, role=serializer.validated_data['role'])
            return Response({'success': 'Role has been successfully updated.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompanySelectionView(APIView):
    permission_classes = [IsAuthenticated]  # write permission only for users with role

    def post(self, request):
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            user_company = UserRoleCompany.objects.get(user=user)
            user_company.company_id = serializer.validated_data['company_id']
            user_company.save()
            return Response({'success': 'Company has been successfully updated.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCompanyView(generics.ListAPIView):
    permission_classes = []  # write permission only for users with role

    def get_serializer_class(self):
        user = UserRoleCompany.objects.get(user=self.request.user)
        user_role = user.role

        if user_role == 'startup':
            return StartupSerializer
        elif user_role == 'investor':
            return InvestorSerializer

    def get_queryset(self):
        user = UserRoleCompany.objects.get(user=self.request.user)
        user_role = user.role

        if user_role == 'startup':
            user_startups = UserStartup.objects.filter(customuser=self.request.user).values('startup')
            return Startup.objects.filter(id__in=user_startups)
        elif user_role == 'investor':
            user_investors = UserInvestor.objects.filter(customuser=self.request.user).values('investor')
            return Investor.objects.filter(id__in=user_investors)


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
            message_data = {
                'subject': 'Verify your email',
                'body': ' Use the link below to verify your email \n'
            }
            Util.send_email(get_current_site(request).domain, 'users:email-verify', new_user, token, message_data)
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
    """
    API endpoint for initiating the password recovery process by sending a recovery email to the user's email address.

    Request Payload:
    - email: The email address of the user requesting password recovery.

    Response:
    - If the email is valid and corresponds to an existing user:
        - Status Code: 200
        - Response Body: {'success': 'Email was sent successfully'}
    - If the email is not valid or does not correspond to any user:
        - Status Code: 400
        - Response Body: {'error': 'User does not exist'}

    Permissions:
    - AllowAny: Publicly accessible endpoint.

    Methods:
    - POST: Initiates the password recovery process by sending a recovery email to the user's email address.

    Example Usage:
    ```
    POST /api/password-recovery/
    {
        "email": "example@example.com"
    }
    ```

    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')

        serializer = RecoveryEmailSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = CustomUser.objects.get(email=email)
                token = RefreshToken.for_user(user).access_token
                message_data = {
                    'subject': 'Password reset link',
                    'body': ' Use the link below to reset your password \n'
                }
                Util.send_email(get_current_site(request).domain, 'users:password-reset', user, token, message_data)
                return Response({'success': 'Email was sent successfully'}, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                #return 200 instead of HTTP_400_BAD_REQUEST
                return Response({'error': 'User does not exist'}, status=status.HTTP_200_OK)
        # return 200 instead of HTTP_400_BAD_REQUEST
        return Response(serializer.errors, status=status.HTTP_200_OK)


class PasswordResetView(APIView):
    """
    API endpoint for resetting the password using a token received via email.

    Permissions:
    - AllowAny: Publicly accessible endpoint.

    Methods:
    - GET: Returns a success response indicating to enter new data for password reset.
    - POST: Validates the token and resets the user's password.

    """
    permission_classes = [AllowAny]

    def get(self, request, token):
        """
        Returns a success response indicating to enter new data for password reset.

        Parameters:
        - request (HttpRequest): The HTTP request object.

        Returns:
        - Response: JSON response indicating the success of the operation.

        """
        return Response({'success': 'Enter a new password and repeat it'}, status=status.HTTP_200_OK)

    def post(self, request, token):
        """
        Validates the token and resets the user's password.

        Parameters:
        - request (HttpRequest): The HTTP request object.
        - token (str): The token received via email for password reset.

        Returns:
        - Response: JSON response indicating the result of the password reset operation.

        """
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            try:
                if not request.user.is_authenticated:
                    payload = jwt.decode(token, settings.SECRET_KEY, settings.SIMPLE_JWT['ALGORITHM'])
                    user = CustomUser.objects.get(id=payload['user_id'])
                    user.set_password(serializer.validated_data.get('password'))
                    user.save()
                    return Response({'success': 'Password has been successfully updated'}, status=status.HTTP_200_OK)
            except jwt.ExpiredSignatureError as identifier:
                return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
            #added CustomUser.DoesNotExist as a sign of invalid token
            except (jwt.exceptions.DecodeError, CustomUser.DoesNotExist):
                return Response({'error': 'Invalid token'}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# boilerplate (for a future "logout" endpoint) to delete the JWT token from cookies
def logout(request):
    response = JsonResponse({"message": "Logged out"})
    response.delete_cookie('jwt_token')  # Delete the JWT cookie
    return response

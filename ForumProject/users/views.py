from rest_framework_simplejwt.exceptions import TokenError
import jwt
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView as BaseTokenObtainPairView,
    TokenRefreshView as BaseTokenRefreshView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from django.http import JsonResponse
from rest_framework.exceptions import ValidationError


from investors.models import Investor
from investors.serializers import InvestorSerializer
from startups.models import Startup
from startups.serializers import StartupSerializer
from .models import CustomUser, UserRoleCompany, UserStartup, UserInvestor
from .permissions import IsRole
from .serializers import (UserRegisterSerializer, RecoveryEmailSerializer, PasswordResetSerializer,
                          RoleSerializer, CompanySerializer)
from .utils import Util


class TokenObtainPairView(BaseTokenObtainPairView):
    """
    Custom view for obtaining JWT token pairs (access token and refresh token).

    Attributes:
        throttle_scope (str): The throttle scope for rate limiting token obtain requests.
    """
    throttle_scope = 'token_obtain'

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to obtain JWT token pairs and set the access token in a cookie.

        Args:
            request (Request): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: The HTTP response object containing the token pairs and cookie.
        """
        response = super().post(request, *args, **kwargs)

        token = response.data.get('access')
        refresh_token = response.data.get('refresh')

        if token:
            # Set the token in a cookie with appropriate settings
            response.set_cookie(
                'jwt_token',
                token,
                max_age=300,  # Token lifetime (5 minutes)
                httponly=True,  # To prevent JavaScript access
                secure=True,  # If using HTTPS
                samesite='Strict',
                # helps prevent Cross-Site Request Forgery (CSRF) attacks and reduces the risk of
                # unauthorized cross-site data exchange
            )
        
        if refresh_token:
            # Set the refresh token in a separate cookie
            response.set_cookie(
                'refresh_token',
                refresh_token,
                max_age=400,
                httponly=True,
                secure=True,
                samesite='Strict',
            )

        return response


class TokenRefreshView(BaseTokenRefreshView):
    """
    Custom view for refreshing JWT access tokens.

    Attributes:
        throttle_scope (str): The throttle scope for rate limiting token refresh requests.
    """
    throttle_scope = 'token_refresh'

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to refresh JWT access tokens and set
        the refreshed access token in a cookie.

        Args:
            request (Request): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: The HTTP response object containing
                      the refreshed access token and cookie.
        """
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
    """
    API endpoint for updating the role of the authenticated user.

    Returns a success message if the role is successfully updated.

    Permissions:
    - The user must be authenticated.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Update the role of the authenticated user.

        Parameters:
        - role (str): The new role(startup/investor) to assign to the user.

        Returns:
        - Response with success message if the role is successfully updated.
        - Response with validation errors if the provided data is invalid.
        """
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            user_role_company = UserRoleCompany.objects.get_or_create(user=user, defaults={
                'role': serializer.validated_data['role']})
            user_role_company[0].role = serializer.validated_data['role']
            user_role_company[0].company_id = None
            user_role_company[0].save()
            return Response({'success': 'Role has been successfully updated.'},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompanySelectionView(APIView):
    """
    API endpoint for selecting a company for the authenticated user.

    Returns a success message if the company is successfully selected.

    Permissions:
    - The user must have the appropriate role to select a company.
    """
    permission_classes = [IsRole]

    def post(self, request):
        """
        Select a company for the authenticated user with the appropriate role.

        Parameters:
        - company_id: The ID of the company to select for the user.

        Returns:
        - Response with success message if the company is successfully selected.
        - Response with validation errors if the provided data is invalid.
        - Response with 404 error if the user or company does not exist.
        - Response with 400 error if the company cannot be selected.
        - Response with 403 error if the user does not have the appropriate role.
        """
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            company = serializer.validated_data['company_id']

            user_role_company = get_object_or_404(UserRoleCompany, user=user)

            if user_role_company.role == 'investor' and get_object_or_404(UserInvestor, customuser=user,
                                                                          investor=company):
                user_role_company.company_id = company
                user_role_company.save()
                return Response({'success': 'The investor company was successfully selected'},
                                status=status.HTTP_200_OK)

            elif user_role_company.role == 'startup' and get_object_or_404(UserStartup, customuser=user,
                                                                           startup=company):
                user_role_company.company_id = company
                user_role_company.save()
                return Response({'success': 'The startup company was successfully selected'},
                                status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCompanyView(generics.ListAPIView):
    """
    API endpoint for retrieving companies associated with the authenticated user.

    Returns a list of companies based on the user's role.

    Permissions:
    - The user must have the appropriate role to access this endpoint.
    """
    permission_classes = [IsRole]

    def get_serializer_class(self):
        """
        Return the serializer class based on the user's role.

        Returns:
        - StartupSerializer if the user has a 'startup' role.
        - InvestorSerializer if the user has an 'investor' role.
        """
        user = get_object_or_404(UserRoleCompany, user=self.request.user)
        user_role = user.role

        if user_role == 'startup':
            return StartupSerializer
        elif user_role == 'investor':
            return InvestorSerializer

    def get_queryset(self):
        """
        Return the queryset of companies based on the user's role.

        Returns:
        - Queryset of startups if the user has a 'startup' role.
        - Queryset of investors if the user has an 'investor' role.
        """
        user = get_object_or_404(UserRoleCompany, user=self.request.user)
        user_role = user.role

        if user_role == 'startup':
            user_startups = UserStartup.objects.filter(customuser=self.request.user).values_list('startup', flat=True)
            return Startup.objects.filter(id__in=user_startups)
        if user_role == 'investor':
            user_investors = UserInvestor.objects.filter(customuser=self.request.user).values_list('investor',
                                                                                                   flat=True)
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
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class PasswordRecoveryView(APIView):
    """
    API endpoint for initiating the password recovery process by sending
    a recovery email to the user's email address.

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
    - POST: Initiates the password recovery process by sending
    a recovery email to the user's email address.

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
        """
        Handle POST requests to send a password reset email.

        This method retrieves the email address from the request data,
        validates it using the RecoveryEmailSerializer,
        and sends a password reset email to the user if the email is valid
        and associated with an existing user account.

        Args:
            request (Request): The HTTP request object containing
            the email address in the data payload.

        Returns:
            Response: The HTTP response object indicating the status of the email sending process.
                - If the email is valid and sent successfully, it returns
                  a success message with status code 200.
                - If the email is invalid or not associated with an existing user account,
                  it returns an error message with status code 200.
                - If there are validation errors in the serializer,
                  it returns the serializer errors with status code 200.
        """
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
                # return 200 instead of HTTP_400_BAD_REQUEST
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
                    return Response({'success': 'Password has been successfully updated'},
                                    status=status.HTTP_200_OK)
            except jwt.ExpiredSignatureError:
                return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
            # added CustomUser.DoesNotExist as a sign of invalid token
            except (jwt.exceptions.DecodeError, CustomUser.DoesNotExist):
                return Response({'error': 'Invalid token'}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()
            response = Response({"message": "User successfully logged out."}, status=status.HTTP_200_OK)
            response.delete_cookie('jwt_token')
            response.delete_cookie('refresh_token')
            return response
        except TokenError:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({"error": "Refresh token not provided."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
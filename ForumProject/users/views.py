from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import (
    TokenObtainPairView as BaseTokenObtainPairView,
    TokenRefreshView as BaseTokenRefreshView,
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed


class TokenObtainPairView(BaseTokenObtainPairView):
    throttle_scope = 'token_obtain'


class TokenRefreshView(BaseTokenRefreshView):
    throttle_scope = 'token_refresh'


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "User successfully logged out."}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({"error": "Refresh token not provided."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log the unexpected error for further investigation
            print(f"Unexpected error: {e}")
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

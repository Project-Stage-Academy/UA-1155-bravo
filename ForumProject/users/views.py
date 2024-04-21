from rest_framework_simplejwt.views import (TokenObtainPairView as BaseTokenObtainPairView,
                                            TokenRefreshView as BaseTokenRefreshView)
from django.http import JsonResponse
from datetime import timedelta


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
                samesite='Strict',  #  helps prevent Cross-Site Request Forgery (CSRF) attacks and reduces the risk of unauthorized cross-site data exchange
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
    

# boilerplate (for a future "logout" endpoint) to delete the JWT token from cookies
def logout(request):
    response = JsonResponse({"message": "Logged out"})
    response.delete_cookie('jwt_token')  # Delete the JWT cookie
    return response

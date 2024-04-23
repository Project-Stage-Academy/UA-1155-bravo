from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout, get_user_model
from django_rest_passwordreset.serializers import PasswordTokenSerializer
from .models import CustomUser
from rest_framework_simplejwt.views import (TokenObtainPairView as BaseTokenObtainPairView,
                                            TokenRefreshView as BaseTokenRefreshView)


class TokenObtainPairView(BaseTokenObtainPairView):
    throttle_scope = 'token_obtain'


class TokenRefreshView(BaseTokenRefreshView):
    throttle_scope = 'token_refresh'


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('login')  # Redirect to logged-in page
        else:
            # Authentication failed, handle error
            pass
    return render(request, 'login.html')


# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.views import APIView
#
# class PasswordRecoveryView(APIView):
#     def post(self, request, *args, **kwargs):
#         serializer = PasswordTokenSerializer(data=request.data)
#         if serializer.is_valid():
#             email = serializer.validated_data.get('email')
#             try:
#                 user = get_user_model().objects.get(email=email)
#                 user.send_password_reset_email(request)
#                 return Response({'detail': 'Password reset email has been sent.'}, status=status.HTTP_200_OK)
#             except ObjectDoesNotExist:
#                 pass
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
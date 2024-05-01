from django.urls import path
from rest_framework.throttling import ScopedRateThrottle

from . import views


app_name = 'users'

urlpatterns = [

    path('token/', views.TokenObtainPairView.as_view(throttle_classes=[ScopedRateThrottle]), name='token_obtain_pair'),
    path('token/refresh/', views.TokenRefreshView.as_view(throttle_classes=[ScopedRateThrottle]), name='token_refresh'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('email-verify/<token>/', views.VerifyEmailView.as_view(), name='email-verify'),
    path('password-recovery/', views.PasswordRecoveryView.as_view(), name='password-recovery'),
    path('password-reset/<token>/', views.PasswordResetView.as_view(), name='password-reset'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]

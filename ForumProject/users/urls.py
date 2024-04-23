from django.urls import path, include
from rest_framework.throttling import ScopedRateThrottle

from . import views

app_name = 'users'

urlpatterns = [
    path('token/', views.TokenObtainPairView.as_view(throttle_classes=[ScopedRateThrottle]), name='token_obtain_pair'),
    path('token/refresh/', views.TokenRefreshView.as_view(throttle_classes=[ScopedRateThrottle]), name='token_refresh'),
    # path('login/', views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('password_recovery/', views.PasswordRecoveryView.as_view(), name='password_recovery'),
]

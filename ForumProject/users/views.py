from rest_framework_simplejwt.views import (TokenObtainPairView as BaseTokenObtainPairView,
                                            TokenRefreshView as BaseTokenRefreshView)


class TokenObtainPairView(BaseTokenObtainPairView):
    throttle_scope = 'token_obtain'


class TokenRefreshView(BaseTokenRefreshView):
    throttle_scope = 'token_refresh'

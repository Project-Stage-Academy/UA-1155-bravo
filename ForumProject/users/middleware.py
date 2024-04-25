class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if a JWT token exists in the cookies
        token = request.COOKIES.get('jwt_token')
        if token:
            # If the token exists, set the Authorization header
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'

        # Proceed with the request
        response = self.get_response(request)

        return response
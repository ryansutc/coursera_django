

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from drf_spectacular.utils import extend_schema

# custom serializers for our endpoints to override the built-in default ones
class CookieTokenObtainPairResponseSerializer(serializers.Serializer):
    access = serializers.CharField()

class CookieTokenRefreshResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
@extend_schema(
    responses={200: CookieTokenObtainPairResponseSerializer}
)
class CookieTokenObtainPairView(TokenObtainPairView):
    '''
    Our override of the simple jwt TokenObtainPairView.
    We choose to set the refresh token in a cookie for better security
    after a user logs in and gets a token
    '''
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        refresh = response.data.get("refresh")
        if refresh:
            response.set_cookie(
                key="refresh_token",
                value=refresh,
                httponly=True,
                secure=not settings.DEBUG,  # True in production, False in development
                samesite="Lax",  # Or "Strict" or "None" as needed
                path="/",  # Or restrict to your refresh endpoint
            )
            # Optionally remove refresh from response body
            del response.data["refresh"]
        return response

@extend_schema(
    responses={200: CookieTokenRefreshResponseSerializer}
) 
class CookieTokenRefreshView(TokenRefreshView):
    '''
    Our override of the simple jwt TokenRefreshView.
    We choose to get the refresh token from the cookie
    instead of the request body when a client/user tries
    to refresh their token.
    '''
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        # Try to get the refresh token from the cookie if not in the body
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token:
            # Make a mutable copy of request.data
            data = request.data.copy()
            data["refresh"] = refresh_token
            request._full_data = data  # Patch the request data for the serializer
        return super().post(request, *args, **kwargs)
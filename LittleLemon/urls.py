"""
URL configuration for LittleLemon project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from graphene_django.views import GraphQLView
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
)
from LittlelemonAPI.views.auth import CookieTokenObtainPairView, CookieTokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("LittlelemonAPI.urls")),
    path("drf/", include("LittleLemonDRF.urls")),  # Include DRF app URLs
    path("auth/", include("djoser.urls")),  # Djoser authentication endpoints
    path("auth/", include("djoser.urls.authtoken")),  # Token authentication endpoints
    path("api/token/", CookieTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path("graphql", csrf_exempt(GraphQLView.as_view(graphiql=True)), name="graphql"),
]

# djoser offers a bunch of endpoints:

# /users/ - list users
# /users/<id>/ - retrieve, update, or delete a user
# /users/me/ - retrieve or update the current user
# /users/activation/ - activate a user account
# /users/reset_password/ - request a password reset
# /users/reset_password_confirm/ - confirm a password reset
# /users/set_password/ - change the password of the current user
# /users/resend_activation/ - resend activation email
# /token/login/ - obtain an authentication token
# /token/logout/ - logout and delete the authentication token
# /users/confirm/ - confirm a user account

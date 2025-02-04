# backend/urls

from django.contrib import admin
from django.urls import path, include
from api.views import CreateUserView
from api.serializers import CustomTokenObtainPairView  # Change this import
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/user/register/", CreateUserView.as_view(), name="register"),
    path("api/token/", CustomTokenObtainPairView.as_view(), name="get_token"),  # Change this line
    path("api/token/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("api-auth/", include("rest_framework.urls")),
    path("api/", include("api.urls")),
]
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import ProtectedAPIView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from .views import (
    UserSignupAPIView,
    CustomLoginAPIView,
    CurrentUserAPIView,
    ForgotPasswordAPIView,
    ResetPasswordAPIView,
    LogoutAPIView,
    ChangePasswordAPIView
)


urlpatterns = [
    path("signup/", UserSignupAPIView.as_view(), name="api_signup"),
    path("login/", CustomLoginAPIView.as_view(), name="api_login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('me/', CurrentUserAPIView.as_view(), name='current_user'),
    path("logout/", LogoutAPIView.as_view(), name="api_logout"),
    path('protected/', ProtectedAPIView.as_view()),
    path('forgot-password/', ForgotPasswordAPIView.as_view()),
    path('reset-password/<uidb64>/<token>/', ResetPasswordAPIView.as_view(), name='reset_password_api'),
    path('change-password/', ChangePasswordAPIView.as_view()),


]

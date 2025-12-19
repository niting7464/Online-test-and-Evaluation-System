from django.urls import path
from .frontend_views import register_view, login_view, dashboard , forgot_password_view , reset_password_view

urlpatterns = [
    path("register/", register_view, name="register_page"),
    path("login/", login_view, name="login_page"),
    path("dashboard/", dashboard, name="dashboard"),
    path("forgot-password/", forgot_password_view, name="forgot-password_page"),
    path("reset-password/<uid>/<token>/", reset_password_view, name="reset-password_page"),
]

from django.urls import path
from .frontend_views import register_view, login_view , forgot_password_view , reset_password_view, logout_view, change_password_view, edit_email_view, health_check

urlpatterns = [
    path("register/", register_view, name="register_page"),
    path("login/", login_view, name="login_page"),
    path("forgot-password/", forgot_password_view, name="forgot-password_page"),
    path("reset-password/<uid>/<token>/", reset_password_view, name="reset-password_page"),
    path("logout/", logout_view, name="logout"),
    path("change-password/", change_password_view, name="change-password_page"),
    path("edit-email/", edit_email_view, name="edit-email_page"),
    path("health/", health_check),
    

    
]

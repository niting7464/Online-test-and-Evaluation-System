from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import authenticate, login as django_login, logout
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib import messages
from .forms import RegisterForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from django.views.decorators.csrf import ensure_csrf_cookie

# API base (used by some frontend views). Prefer internal auth where possible.
API_BASE_URL = "http://127.0.0.1:8000/api/auth"
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives

# NOTE: avoid making HTTP requests to the same Django process (deadlock).
# Frontend views should authenticate internally instead of calling the API.


@ensure_csrf_cookie
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            User = get_user_model()
            try:
                User.objects.create_user(username=data['username'], email=data['email'], password=data['password'])
            except IntegrityError:
                form.add_error(None, "Username or email already exists")
                return render(request, "auth/register.html", {"form": form})

            messages.success(request, "Registration successful. Please login.")
            return redirect(f"{reverse('login_page')}?registered=1")
        else:
            return render(request, "auth/register.html", {"form": form})

    return render(request, "auth/register.html")



@ensure_csrf_cookie
def login_view(request):
    # Show a success message when redirected after registration
    if request.method == "GET" and request.GET.get('registered'):
        messages.success(request, "Registration successful. You can login now. <a href='#login-form' class='cta-dismiss btn btn-sm btn-primary ms-2'>Go to Login</a>")
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']

            # Log the user in first (creates session auth)
            django_login(request, user)

            # Create JWT tokens for API usage and store minimal info in session
            try:
                refresh = RefreshToken.for_user(user)
                access = str(refresh.access_token)
                request.session["access"] = access
                request.session["refresh"] = str(refresh)
            except Exception:
                # token generation shouldn't block login
                pass

            request.session["user_id"] = user.id

            messages.success(request, "Logged in successfully")
            return redirect(reverse('dashboard'))
        else:
            return render(request, "auth/login.html", {"form": form})

    return render(request, "auth/login.html")


@ensure_csrf_cookie
def forgot_password_view(request):
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            User = get_user_model()
            user = User.objects.filter(email=email).first()

            # Prevent enumeration
            if user:
                token = PasswordResetTokenGenerator().make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_link = f"http://127.0.0.1:8000/reset-password/{uid}/{token}/"
                html_content = render_to_string(
                    "emails/password_reset.html",
                    {"user": user, "reset_link": reset_link}
                )
                text_content = strip_tags(html_content)
                email_message = EmailMultiAlternatives(
                    subject="Reset Your Password",
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[email],
                )
                email_message.attach_alternative(html_content, "text/html")
                email_message.send()

            messages.success(request, "If the email exists, a reset link has been sent")
            return redirect("forgot-password_page")
        else:
            return render(request, "auth/forgot_password.html", {"form": form})

    return render(request, "auth/forgot_password.html")


@ensure_csrf_cookie
def reset_password_view(request, uid, token):
    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            try:
                uid_decoded = force_str(urlsafe_base64_decode(uid))
                User = get_user_model()
                user = User.objects.get(pk=uid_decoded)
            except Exception:
                messages.error(request, "Invalid reset link")
                return render(request, "auth/reset_password.html", {"form": form})

            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.error(request, "Reset link is invalid or expired")
                return render(request, "auth/reset_password.html", {"form": form})

            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Password reset successful. Please login.")
            return redirect("login_page")
        else:
            return render(request, "auth/reset_password.html", {"form": form})

    return render(request, "auth/reset_password.html")


def logout_view(request):
    # ensure Django auth session is cleared too
    try:
        logout(request)
    except Exception:
        pass
    request.session.flush()
    return redirect("/login/")









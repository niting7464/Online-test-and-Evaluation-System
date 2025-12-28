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
import logging
from threading import Thread

# NOTE: avoid making HTTP requests to the same Django process (deadlock).
# Frontend views should authenticate internally instead of calling the API.

from django.http import JsonResponse


def health_check(request):
    return JsonResponse({"status": "ok"})


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



logger = logging.getLogger(__name__)

def send_reset_email(user, reset_link):
    """
    Send the password reset email using Brevo API.
    """
    api_key = settings.BREVO_API_KEY  # Add this in your Render environment
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "Content-Type": "application/json"
    }

    # Render your HTML email template
    html_content = render_to_string("emails/password_reset.html", {"user": user, "reset_link": reset_link})
    
    # Send POST request to Brevo API
    payload = {
        "sender": {"name": "Online Test System", "email": settings.DEFAULT_FROM_EMAIL},
        "to": [{"email": user.email, "name": user.get_full_name() or user.username}],
        "subject": "Reset Your Password",
        "htmlContent": html_content
    }

    response = requests.post(url, json=payload, headers=headers, timeout=10)
    if response.status_code != 201:
        logger.error(f"Brevo email failed: {response.status_code} {response.text}")
        raise Exception(f"Failed to send email: {response.status_code} {response.text}")


@ensure_csrf_cookie
def forgot_password_view(request):
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            User = get_user_model()
            user = User.objects.filter(email=email).first()

            if user:
                try:
                    token = PasswordResetTokenGenerator().make_token(user)
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    reset_path = reverse('reset-password_page', args=[uid, token])

                    domain = getattr(settings, 'PASSWORD_RESET_DOMAIN', None)
                    if domain:
                        reset_link = domain.rstrip('/') + reset_path
                    else:
                        reset_link = request.build_absolute_uri(reset_path)

                    send_reset_email(user, reset_link)

                except Exception as e:
                    logger.error(f"Failed to send password reset email: {e}")

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


@ensure_csrf_cookie
def change_password_view(request):
    """
    Frontend handler for changing password from dashboard.
    Uses session-based auth (expects user_id in session) and Django user check_password.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")

    User = get_user_model()
    user = User.objects.filter(id=user_id).first()
    if not user:
        return redirect("login_page")

    if request.method == "POST":
        old = request.POST.get('old_password')
        new = request.POST.get('new_password')
        confirm = request.POST.get('confirm_password')

        if not old or not new or not confirm:
            messages.error(request, "All fields are required")
            return redirect(reverse('dashboard'))

        if new != confirm:
            messages.error(request, "New passwords do not match")
            return redirect(reverse('dashboard'))

        if not user.check_password(old):
            messages.error(request, "Old password is incorrect")
            return redirect(reverse('dashboard'))

        user.set_password(new)
        user.save()
        messages.success(request, "Password changed successfully")
        return redirect(reverse('dashboard'))
    # For GET, render change password page
    return render(request, 'auth/change_password.html')


@ensure_csrf_cookie
def edit_email_view(request):
    """Frontend handler to change user's email from dashboard/profile dropdown."""
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")

    User = get_user_model()
    user = User.objects.filter(id=user_id).first()
    if not user:
        return redirect("login_page")

    if request.method == "POST":
        old_email = request.POST.get('old_email')
        new_email = request.POST.get('new_email')
        if not old_email or not new_email:
            messages.error(request, "Both current and new email are required")
            return redirect(reverse('dashboard'))

        # verify old email matches current
        if old_email.strip().lower() != (user.email or '').strip().lower():
            messages.error(request, "Current email does not match")
            return redirect(reverse('dashboard'))

        # check uniqueness
        existing = User.objects.filter(email__iexact=new_email.strip()).exclude(id=user.id).first()
        if existing:
            messages.error(request, "Email already in use")
            return redirect(reverse('dashboard'))

        user.email = new_email.strip()
        user.save()
        messages.success(request, "Email updated successfully")
        return redirect(reverse('dashboard'))
    # For GET, render edit email page
    return render(request, 'auth/edit_email.html', { 'current_email': user.email })


def logout_view(request):
    # ensure Django auth session is cleared too
    try:
        logout(request)
    except Exception:
        pass
    request.session.flush()
    return redirect("/login/")









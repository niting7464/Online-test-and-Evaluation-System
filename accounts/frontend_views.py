import requests
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse

API_BASE_URL = "http://127.0.0.1:8000/api/auth"


def register_view(request):
    if request.method == "POST":
        payload = {
            "username": request.POST.get("username"),
            "email": request.POST.get("email"),
            "password": request.POST.get("password"),
            "confirm_password": request.POST.get("confirm_password"),
        }

        response = requests.post(f"{API_BASE_URL}/signup/", json=payload)

        if response.status_code == 201:
            return redirect("login_page")

        error = response.json()
        return render(request, "auth/register.html", {"error": error})

    return render(request, "auth/register.html")


def login_view(request):
    if request.method == "POST":
        payload = {
            "username_or_email": request.POST.get("username_or_email"),
            "password": request.POST.get("password"),
        }

        response = requests.post(f"{API_BASE_URL}/login/", json=payload)
        
        print(request.session.get("access"))


        if response.status_code == 200:
            data = response.json()
            request.session["access"] = data["access"]
            request.session["refresh"] = data["refresh"]
            return redirect("dashboard")  # future page


        return render(
            request,
            "auth/login.html",
            {"error": "Invalid credentials"}
        )

    return render(request, "auth/login.html")


def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get("email")

        response = requests.post(
            f"{API_BASE_URL}/forgot-password/",
            json={"email": email}
        )

        if response.status_code == 200:
            return render(
                request,
                "auth/forgot_password.html",
                {"message": "Password reset link sent to your email."}
            )

        return render(
            request,
            "auth/forgot_password.html",
            {"error": "Email not found."}
        )

    return render(request, "auth/forgot_password.html")


def reset_password_view(request, uid, token):
    if request.method == "POST":
        payload = {
            "password": request.POST.get("password"),
            "confirm_password": request.POST.get("confirm_password"),
        }

        response = requests.post(
            f"{API_BASE_URL}/reset-password/{uid}/{token}/",
            json=payload
        )

        if response.status_code == 200:
            return redirect("login_page")

        return render(
            request,
            "auth/reset_password.html",
            {"error": response.json().get("error")}
        )

    return render(request, "auth/reset_password.html")



def dashboard(request):
    return HttpResponse("Login successful")






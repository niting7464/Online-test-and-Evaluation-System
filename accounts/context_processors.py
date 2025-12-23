from django.conf import settings
import requests

API_BASE_URL = getattr(settings, "API_BASE_URL", "http://127.0.0.1:8000/api/auth")

def auth_user(request):
    """
    Adds 'current_user' to templates based on session tokens.
    """
    user_info = None
    access = request.session.get("access")

    if access:
        try:
            response = requests.get(
                f"{API_BASE_URL}/me/",  # endpoint returning logged-in user info
                headers={"Authorization": f"Bearer {access}"}
            )
            if response.status_code == 200:
                user_info = response.json()
        except Exception:
            pass

    return {"current_user": user_info}

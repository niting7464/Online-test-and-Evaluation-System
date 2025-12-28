import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_reset_email(email, reset_link):
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "api-key": settings.BREVO_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {
        "sender": {"email": settings.DEFAULT_FROM_EMAIL},
        "to": [{"email": email}],
        "subject": "Reset Your Password",
        "htmlContent": f"""
            <p>Click the link below to reset your password:</p>
            <a href="{reset_link}">{reset_link}</a>
        """
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Brevo email failed: {e}")

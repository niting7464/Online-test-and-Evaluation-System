from django.utils.functional import SimpleLazyObject
from django.contrib.auth import get_user_model


def get_user_from_session(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    User = get_user_model()
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None


class SessionUserMiddleware:
    """Set request.user from session['user_id'] if JWT login is used."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # preserve any existing user value to avoid recursive lookup
        original_user = getattr(request, "user", None)
        request.user = SimpleLazyObject(lambda: get_user_from_session(request) or original_user)
        response = self.get_response(request)
        return response

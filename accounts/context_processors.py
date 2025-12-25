from django.contrib.auth import get_user_model


def current_user(request):
    """Context processor that exposes `current_user` to templates.

    It prefers `request.user` (set by authentication or SessionUserMiddleware),
    but will attempt to resolve from session['user_id'] as a fallback.
    """
    user = None
    try:
        user = getattr(request, "user", None)
    except Exception:
        user = None

    if user and getattr(user, "is_authenticated", False):
        return {"current_user": user}

    # fallback: try to resolve from session
    user_id = request.session.get("user_id")
    if not user_id:
        return {"current_user": None}

    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        user = None

    return {"current_user": user}


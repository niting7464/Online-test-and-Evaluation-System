from django.shortcuts import render, redirect, get_object_or_404
import json
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import TestAttempt, Test
from .serializers import TestResultSerializer, StartTestSerializer


def start_attempt_view(request, test_id):
    """Create a TestAttempt for the logged-in user and redirect to attempt page."""
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")

    User = get_user_model()
    user = User.objects.filter(id=user_id).first()
    if not user:
        return redirect("login_page")

    serializer = StartTestSerializer(data={"test_id": test_id}, context={"request": request})
    try:
        serializer.is_valid(raise_exception=True)
        attempt = serializer.save()
    except Exception as e:
        messages.error(request, str(e))
        return redirect("dashboard")

    return redirect(reverse('test-attempt', args=[attempt.id]))


def dashboard_view(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")

    # Try to resolve the actual User instance from session
    User = get_user_model()
    current_user = User.objects.filter(id=user_id).first()
    if not current_user:
        return redirect("login_page")

    tests = Test.objects.filter(status="PUBLISHED")
    completed_attempts = TestAttempt.objects.filter(
        user_id=user_id,
        status="COMPLETED"
    )
    attempt_count = completed_attempts.count()

    # optional highlight attempt id from querystring
    highlight_attempt = request.GET.get('highlight')

    return render(request, "dashboard/dashboard.html", {
        "tests": tests,
        "completed_attempts": completed_attempts,
        "current_user": current_user,
        "highlight_attempt": highlight_attempt,
        "attempt_count": attempt_count,
    })


def test_attempt_view(request, attempt_id, index=None):
    """
    Page for attempting a test.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")


    attempt = get_object_or_404(TestAttempt, id=attempt_id, user_id=user_id)

    serializer = TestResultSerializer(attempt)

    # calculate remaining seconds for client timer
    started = attempt.started_at
    duration_seconds = attempt.test.duration * 60
    elapsed = (timezone.now() - started).total_seconds()
    remaining = int(max(0, duration_seconds - elapsed))

    return render(request, "test/attempt.html", {
        "attempt": attempt,
        "categories": serializer.data["categories"],
        "remaining_seconds": remaining,
        "selected_category_index": int(index) if index is not None else None,
    })



def test_result_view(request, attempt_id):
    """
    Test result page.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login_page")


    attempt = TestAttempt.objects.get(
        id=attempt_id,
        user_id=user_id
    )

    serializer = TestResultSerializer(attempt)
    result_data = serializer.data
    return render(request, "test/result.html", {
        "result": result_data,
        "result_json": json.dumps(result_data),
        "attempt_id": attempt.id,
    })

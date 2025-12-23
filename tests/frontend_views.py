from django.shortcuts import render, redirect
from accounts.decorators import jwt_login_required
from .models import TestAttempt, Test
from .serializers import TestResultSerializer

@jwt_login_required
def dashboard_view(request):
    """
    Dashboard showing ongoing and completed tests.
    """
    user_id = request.session.get("user_id")
    username = request.session.get("username")  # for template display

    # All available published tests
    tests = Test.objects.filter(status="PUBLISHED")

    # Completed attempts of the logged-in user
    completed_attempts = TestAttempt.objects.filter(
        user_id=user_id,
        status="COMPLETED"
    )

    return render(request, "dashboard/dashboard.html", {
        "current_user": {"username": username},
        "tests": tests,
        "completed_attempts": completed_attempts
    })


@jwt_login_required
def test_attempt_view(request, attempt_id):
    """
    Page for attempting a test.
    """
    user_id = request.session.get("user_id")

    attempt = TestAttempt.objects.get(
        id=attempt_id,
        user_id=user_id
    )

    serializer = TestResultSerializer(attempt)
    return render(request, "test/attempt.html", {
        "attempt": attempt,
        "categories": serializer.data["categories"]
    })


@jwt_login_required
def test_result_view(request, attempt_id):
    """
    Test result page.
    """
    user_id = request.session.get("user_id")

    attempt = TestAttempt.objects.get(
        id=attempt_id,
        user_id=user_id
    )

    serializer = TestResultSerializer(attempt)
    return render(request, "test/result.html", {
        "result": serializer.data
    })

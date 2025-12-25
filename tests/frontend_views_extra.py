from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from .models import TestAttempt


def attempted_tests_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login_page')

    User = get_user_model()
    user = User.objects.filter(id=user_id).first()
    if not user:
        return redirect('login_page')

    attempts = TestAttempt.objects.filter(user_id=user_id).order_by('-started_at')
    return render(request, 'dashboard/attempted_tests.html', {'attempts': attempts})

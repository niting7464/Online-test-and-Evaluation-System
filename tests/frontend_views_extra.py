from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F, Case, When
from .models import TestAttempt


def attempted_tests_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login_page')

    User = get_user_model()
    user = User.objects.filter(id=user_id).first()
    if not user:
        return redirect('login_page')

    # Sort: completed attempts by completed_at (latest first), ongoing by started_at (latest first)
    attempts = TestAttempt.objects.filter(user_id=user_id).annotate(
        sort_date=Case(
            When(status='COMPLETED', then=F('completed_at')),
            default=F('started_at'),
            output_field=models.DateTimeField()
        )
    ).order_by('-sort_date', '-started_at')
    
    return render(request, 'dashboard/attempted_tests.html', {'attempts': attempts})

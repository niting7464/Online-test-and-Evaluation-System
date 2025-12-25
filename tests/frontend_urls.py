from django.urls import path
from .frontend_views import (
    dashboard_view,
    start_attempt_view,
    test_attempt_view,
    test_result_view,
)
from .frontend_views_extra import attempted_tests_view

urlpatterns = [
    path("dashboard/", dashboard_view, name="dashboard"),
    path("start/<int:test_id>/", start_attempt_view, name="start-attempt"),
    path("attempt/<int:attempt_id>/", test_attempt_view, name="test-attempt"),
    path("attempt/<int:attempt_id>/category/<int:index>/", test_attempt_view, name="test-attempt-category"),
    path("result/<int:attempt_id>/", test_result_view, name="test-result"),
    path("attempted/", attempted_tests_view, name="attempted-tests"),
]

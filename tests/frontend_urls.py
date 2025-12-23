from django.urls import path
from .frontend_views import (
    dashboard_view,
    test_attempt_view,
    test_result_view,
)

urlpatterns = [
    path("dashboard/", dashboard_view, name="dashboard"),
    path("attempt/<int:attempt_id>/", test_attempt_view, name="test-attempt"),
    path("result/<int:attempt_id>/", test_result_view, name="test-result"),
]

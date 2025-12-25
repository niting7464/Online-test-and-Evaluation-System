from django.urls import path
from .views import (

                    StartTestAPIView,
                    FetchAttemptQuestionsAPIView ,
                    SubmitAnswerAPIView,
                    SubmitTestAPIView,
                    TestResultAPIView,
                    ExportAttemptCSVAPIView,
                    )


urlpatterns = [
    path("tests/<int:test_id>/start/", StartTestAPIView.as_view(), name="start-test"),
    path("attempts/<int:attempt_id>/questions/", FetchAttemptQuestionsAPIView.as_view(), name="fetch-attempt-questions"),
    path("attempts/submit-answer/", SubmitAnswerAPIView.as_view(), name="submit-answer"),
    path("attempts/<int:attempt_id>/submit/", SubmitTestAPIView.as_view(), name="submit-test"),
    path("attempts/<int:attempt_id>/export/", ExportAttemptCSVAPIView.as_view(), name="export-attempt"),
    path("attempts/<int:attempt_id>/result/", TestResultAPIView.as_view(), name="test-result"),
]

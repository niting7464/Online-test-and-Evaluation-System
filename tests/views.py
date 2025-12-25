from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Test, TestCategoryConfig , QuestionCategory, Question, TestAttempt, AttemptCategory, UserAnswer
from .serializers import (
    TestCreateSerializer,
    TestCategoryConfigSerializer,
    PublishTestSerializer,
    QuestionCategorySerializer,
    UnpublishTestSerializer,
    QuestionSerializer,
    StartTestSerializer,
    AttemptCategoryQuestionSerializer,
    SubmitAnswerSerializer,
    SubmitTestSerializer,
    TestResultSerializer,
    AdminTestResultSerializer
)
from .permissions import IsAdminUser, IsSystemAdmin , IsNormalUser
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.http import StreamingHttpResponse
import csv
import csv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser 
from django.db.models import Q
from .models import TestAttempt
from .pagination import AdminResultsPagination




class AdminTestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestCreateSerializer

    # Existing unpublish action
    @action(detail=True, methods=["post"])
    def unpublish(self, request, pk=None):
        test = self.get_object()
        if test.status != "PUBLISHED":
            return Response(
                {"detail": "Only published tests can be unpublished"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        test.status = "DRAFT"
        test.save()
        return Response(
            {"message": "Test moved back to draft"},
            status=status.HTTP_200_OK,
        )

    # Updated publish action
    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        test = self.get_object()

        # ✅ Prevent re-publishing
        if test.status == "PUBLISHED":
            return Response(
                {"detail": "Test is already published. Unpublish it first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate category configs and total questions
        serializer = PublishTestSerializer(data=request.data, context={"test": test})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Test published successfully"},
            status=status.HTTP_200_OK,
        )


class AdminTestCategoryConfigViewSet(viewsets.ModelViewSet):
    """
    Handles:
    - Add category to test
    - Update category question count
    - Remove category from test
    """

    serializer_class = TestCategoryConfigSerializer
    permission_classes = [IsSystemAdmin]

    def get_queryset(self):
        return TestCategoryConfig.objects.filter(
            test_id=self.kwargs["test_id"]
        )

    def perform_create(self, serializer):
        test = get_object_or_404(Test, id=self.kwargs["test_id"])
        serializer.save(test=test)
        
        
class AdminQuestionCategoryViewSet(viewsets.ModelViewSet):
    queryset = QuestionCategory.objects.all()
    serializer_class = QuestionCategorySerializer
    permission_classes = [IsSystemAdmin]
    
    
class PublishTestAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, test_id):
        test = get_object_or_404(Test, id=test_id)
        serializer = PublishTestSerializer(data=request.data, context={'test': test})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Test published successfully"}, status=status.HTTP_200_OK)


class UnpublishTestAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, test_id):
        test = get_object_or_404(Test, id=test_id)
        serializer = UnpublishTestSerializer(data=request.data, context={'test': test})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Test unpublished successfully"}, status=status.HTTP_200_OK)
    
    
class AdminQuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        category_id = self.request.query_params.get("category")
        if category_id:
            queryset = queryset.filter(question_category_id=category_id)

        return queryset
    
    @action(detail=False, methods=["get"])
    def by_category(self, request):
        category_id = request.query_params.get("category_id")
        questions = self.queryset.filter(question_category_id=category_id)
        serializer = self.get_serializer(questions, many=True)
        return Response(serializer.data)
    
    
class StartTestAPIView(APIView):
    permission_classes = [IsAuthenticated , IsNormalUser]

    def post(self, request, test_id):
        serializer = StartTestSerializer(data={"test_id": test_id}, context={"request": request})
        serializer.is_valid(raise_exception=True)
        attempt = serializer.save()

        # Use correct related name
        for config in attempt.test.category_configs.all():  # <-- change here
            attempt_category = AttemptCategory.objects.create(
                attempt=attempt,
                category=config.category
            )
            questions = config.category.category_questions.filter(is_active=True)[:config.number_of_questions]
            attempt_category.question_set.set(questions)

        return Response({
            "attempt_id": attempt.id,
            "message": "Test started successfully."
        }, status=status.HTTP_201_CREATED)



class FetchAttemptQuestionsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, attempt_id):
        attempt = TestAttempt.objects.get(id=attempt_id, user=request.user)

        # 🔴 ADD THIS
        if attempt.status == "COMPLETED":
            return Response(
                {"detail": "Test already completed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if attempt.is_time_over():
            attempt.status = "COMPLETED"
            attempt.completed_at = timezone.now()
            attempt.save()
            return Response(
                {"detail": "Test time is over."},
                status=status.HTTP_400_BAD_REQUEST
            )

        categories = attempt.categories.all()
        serializer = AttemptCategoryQuestionSerializer(categories, many=True)
        return Response(serializer.data)

    
    
class SubmitAnswerAPIView(APIView):
    permission_classes = [IsAuthenticated, IsNormalUser]

    def post(self, request):
        user = request.user
        attempt_id = request.data.get("attempt")
        question_id = request.data.get("question")
        selected_option = request.data.get("selected_option")

        # 🔹 Validate payload
        if not attempt_id or not question_id or not selected_option:
            return Response(
                {"detail": "attempt, question and selected_option are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔹 Fetch attempt
        try:
            attempt = TestAttempt.objects.get(id=attempt_id, user=user)
        except TestAttempt.DoesNotExist:
            return Response(
                {"detail": "Test attempt not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 🔴 Block if already submitted
        if attempt.status == "COMPLETED":
            return Response(
                {"detail": "Test already submitted."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔴 Auto-complete if time over
        if attempt.is_time_over():
            attempt.status = "COMPLETED"
            attempt.completed_at = timezone.now()
            attempt.save()

            return Response(
                {"detail": "Test time is over. Test auto-submitted."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔹 Fetch question
        try:
            question = Question.objects.get(id=question_id, is_active=True)
        except Question.DoesNotExist:
            return Response(
                {"detail": "Question not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 🔹 Ensure question belongs to this attempt
        if not attempt.categories.filter(question_set=question).exists():
            return Response(
                {"detail": "Question does not belong to this test attempt."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔹 Save or update answer
        is_correct = selected_option == question.correct_option
        # Save selected option and correctness
        answer, _ = UserAnswer.objects.update_or_create(
            attempt=attempt,
            question=question,
            defaults={"selected_option": selected_option, "is_correct": is_correct}
        )
        marks_awarded = question.marks if is_correct else 0

        return Response({
            "message": "Answer saved successfully.",
            "attempt_id": attempt.id,
            "question_id": question.id,
            "selected_option": selected_option,
            "is_correct": is_correct,
            "marks_awarded": marks_awarded,
            "time_left": attempt.time_left()
        }, status=200)

    
    
class SubmitTestAPIView(APIView):
    permission_classes = [IsAuthenticated , IsNormalUser]

    def post(self, request, attempt_id):
        serializer = SubmitTestSerializer(
            data={"attempt_id": attempt_id},
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        attempt = serializer.save()
        # If the client expects HTML (regular browser form submit), redirect
        # to the frontend result page explicitly to avoid name collisions
        accept = request.META.get('HTTP_ACCEPT', '')
        if 'text/html' in accept:
            return redirect(f'/result/{attempt.id}/')

        return Response({
            "message": "Test submitted successfully.",
            "attempt_id": attempt.id,
            "score": attempt.score,
            "status": attempt.status,
            "result_status": attempt.calculate_pass_fail()
        }, status=status.HTTP_200_OK)


        
        
class TestResultAPIView(APIView):
    permission_classes = [IsAuthenticated , IsNormalUser]

    def get(self, request, attempt_id):
        try:
            attempt = TestAttempt.objects.get(id=attempt_id, user=request.user)
        except TestAttempt.DoesNotExist:
            return Response({"detail": "Test attempt not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = TestResultSerializer(attempt)
        return Response(serializer.data, status=status.HTTP_200_OK)
    



class AdminTestResultsAPIView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]

    def get(self, request):
        queryset = TestAttempt.objects.filter(status="COMPLETED").select_related(
            "user", "test"
        )

        # 🔹 Filters
        test_id = request.query_params.get("test")
        user_id = request.query_params.get("user")
        result = request.query_params.get("result")  # pass / fail

        if test_id:
            queryset = queryset.filter(test_id=test_id)

        if user_id:
            queryset = queryset.filter(user_id=user_id)

        if result == "pass":
            queryset = [
                attempt for attempt in queryset
                if attempt.calculate_pass_fail()["passed"]
            ]
        elif result == "fail":
            queryset = [
                attempt for attempt in queryset
                if not attempt.calculate_pass_fail()["passed"]
            ]

        # 🔹 Pagination
        paginator = AdminResultsPagination()
        page = paginator.paginate_queryset(queryset, request)

        serializer = AdminTestResultSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class AdminTestResultsCSVExportAPIView(APIView):
    permission_classes = [IsAuthenticated,IsAdminUser]

    def get(self, request):
        attempts = TestAttempt.objects.all().order_by("-started_at")

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="test_attempts.csv"'

        writer = csv.writer(response)
        # Header
        writer.writerow([
            "ID", "User", "Test", "Score", "Max Score", "Percentage",
            "Status", "Passed", "Time Taken", "Started At", "Completed At"
        ])

        for attempt in attempts:
            max_score = sum(category.question_set.count() for category in attempt.categories.all())
            percentage = round((attempt.score / max_score) * 100, 2) if max_score > 0 else 0
            passed = percentage >= getattr(attempt.test, "passing_percentage", 40)
            time_taken = ""
            if attempt.completed_at:
                total_seconds = int((attempt.completed_at - attempt.started_at).total_seconds())
                minutes, seconds = divmod(total_seconds, 60)
                time_taken = f"{minutes} min {seconds} sec"

            writer.writerow([
                attempt.id,
                attempt.user.username,
                attempt.test.name,
                attempt.score,
                max_score,
                percentage,
                attempt.status,
                "PASS" if passed else "FAIL",
                time_taken,
                attempt.started_at,
                attempt.completed_at
            ])


class ExportAttemptCSVAPIView(APIView):
    """Export a single attempt as CSV for the attempt owner or admins."""
    permission_classes = [IsAuthenticated,]

    def get(self, request, attempt_id):
        try:
            attempt = TestAttempt.objects.get(id=attempt_id)
        except TestAttempt.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        # only owner or staff can export
        user = request.user
        if not (user.is_staff or attempt.user_id == user.id):
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        # build CSV
        import io
        def stream():
            out = io.StringIO()
            writer = csv.writer(out)
            # Attempt summary header
            writer.writerow(["ID","User","Test","Score","Max Score","Percentage","Status","Passed","Time Taken","Started At","Completed At"])
            yield out.getvalue(); out.seek(0); out.truncate(0)

            max_score = sum(category.question_set.count() for category in attempt.categories.all())
            percentage = round((attempt.score / max_score) * 100, 2) if max_score > 0 else 0
            passed = attempt.calculate_pass_fail()["passed"]
            time_taken = ""
            if attempt.completed_at:
                total_seconds = int((attempt.completed_at - attempt.started_at).total_seconds())
                minutes, seconds = divmod(total_seconds, 60)
                time_taken = f"{minutes} min {seconds} sec"
            writer.writerow([attempt.id, attempt.user.username, attempt.test.name, attempt.score, max_score, percentage, attempt.status, "PASS" if passed else "FAIL", time_taken, attempt.started_at, attempt.completed_at])
            yield out.getvalue(); out.seek(0); out.truncate(0)

            # Per-question details
            writer.writerow([])
            writer.writerow(["Question ID","Question Text","Selected Option","Selected Value","Correct Option","Correct Value","Is Correct","Marks"])
            yield out.getvalue(); out.seek(0); out.truncate(0)

            # collect questions in attempt order
            questions = []
            for cat in attempt.categories.prefetch_related('question_set'):
                for q in cat.question_set.all().distinct():
                    if q.id not in [x.id for x in questions]:
                        questions.append(q)

            for q in questions:
                ans = attempt.answers.filter(question=q).first()
                sel = ans.selected_option if ans else ''
                sel_text = ''
                if sel == 'A': sel_text = q.option_a
                elif sel == 'B': sel_text = q.option_b
                elif sel == 'C': sel_text = q.option_c
                elif sel == 'D': sel_text = q.option_d
                corr = q.correct_option
                corr_text = q.option_a if corr=='A' else (q.option_b if corr=='B' else (q.option_c if corr=='C' else q.option_d))
                is_corr = 'TRUE' if ans and ans.is_correct else 'FALSE'
                writer.writerow([q.id, q.question_text, sel, sel_text, corr, corr_text, is_corr, q.marks])
                yield out.getvalue(); out.seek(0); out.truncate(0)

        filename = f"attempt_{attempt.id}.csv"
        response = StreamingHttpResponse(stream(), content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

        return response
    
    



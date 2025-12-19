from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Test, TestCategoryConfig , QuestionCategory
from .serializers import (
    TestCreateSerializer,
    TestCategoryConfigSerializer,
    PublishTestSerializer,
    QuestionCategorySerializer,
    UnpublishTestSerializer
)
from .permissions import IsAdminUser, IsSystemAdmin
from rest_framework.views import APIView



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

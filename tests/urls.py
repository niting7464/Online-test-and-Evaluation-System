from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminTestViewSet, AdminTestCategoryConfigViewSet , AdminQuestionCategoryViewSet


router = DefaultRouter()
router.register("tests", AdminTestViewSet, basename="admin-tests")
router.register("categories", AdminQuestionCategoryViewSet, basename="admin-categories")


urlpatterns = [
    path("", include(router.urls)),

    path(
        "tests/<int:test_id>/categories/",
        AdminTestCategoryConfigViewSet.as_view({
            "post": "create",
            "get": "list",
        }),
    ),
    path(
        "tests/<int:test_id>/categories/<int:pk>/",
        AdminTestCategoryConfigViewSet.as_view({
            "put": "update",
            "delete": "destroy",
            "patch": "partial_update",
        }),
    ),
]

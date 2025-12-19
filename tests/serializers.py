from rest_framework import serializers
from .models import Test, TestCategoryConfig , QuestionCategory



class QuestionCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionCategory
        fields = ["id", "name"]


class TestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = [
            "id",
            "name",
            "description",
            "duration",
            "max_questions",
            "total_marks",
            "passing_marks",
            "status",
            "created_at",
        ]
        read_only_fields = ["status", "created_at"]

    def validate(self, attrs):
        total_marks = attrs.get("total_marks")
        passing_marks = attrs.get("passing_marks")
        duration = attrs.get("duration")

        if duration is not None and duration <= 0:
            raise serializers.ValidationError(
                {"duration": "Duration must be greater than 0"}
            )

        if (
            total_marks is not None
            and passing_marks is not None
            and passing_marks > total_marks
        ):
            raise serializers.ValidationError(
                {"passing_marks": "Passing marks cannot exceed total marks"}
            )

        return attrs
    
    
    
class TestCategoryConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCategoryConfig
        fields = [
            "id",
            "category",
            "number_of_questions",
        ]

    def validate_number_of_questions(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Number of questions must be greater than 0"
            )
        return value



class PublishTestSerializer(serializers.Serializer):
    def validate(self, attrs):
        test = self.context["test"]

        # Check if test is already published
        if test.status == "PUBLISHED":
            raise serializers.ValidationError("Test is already published. Unpublish it first.")

        category_configs = test.category_configs.all()

        # Check if there is at least one category config
        if not category_configs.exists():
            raise serializers.ValidationError(
                "Cannot publish test without category configuration"
            )

        # Check if sum of category questions equals max_questions
        total_questions = sum(config.number_of_questions for config in category_configs)
        if total_questions != test.max_questions:
            raise serializers.ValidationError(
                f"Total category questions ({total_questions}) "
                f"must equal max questions ({test.max_questions})"
            )

        return attrs

    def save(self, **kwargs):
        test = self.context["test"]
        test.status = "PUBLISHED"
        test.save()
        return test



class UnpublishTestSerializer(serializers.Serializer):
    def validate(self, attrs):
        test = self.context['test']
        if test.status != 'PUBLISHED':
            raise serializers.ValidationError("Only published tests can be unpublished")
        return attrs

    def save(self, **kwargs):
        test = self.context['test']
        test.status = 'DRAFT'
        test.save()
        return test



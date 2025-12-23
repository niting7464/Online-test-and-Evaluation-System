from rest_framework import serializers
from .models import Test, TestCategoryConfig , QuestionCategory, TestAttempt, AttemptCategory, Question, UserAnswer
from django.utils import timezone
from datetime import timedelta




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
    category_name = serializers.SerializerMethodField()
    class Meta:
        model = TestCategoryConfig
        fields = [
            "id",
            "category",
            "category_name",
            "number_of_questions",
        ]
        
    def get_category_name(self, obj):  # <-- method must exist in this class
        return obj.category.name if obj.category else None

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
    

class QuestionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="question_category.name",
        read_only=True
    )

    class Meta:
        model = Question
        fields = [
            "id",
            "question_category",
            "category_name",
            "question_text",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "correct_option",
            "marks",
            "answer_explanation",
        ]

    def validate_marks(self, value):
        if value <= 0:
            raise serializers.ValidationError("Marks must be greater than 0")
        return value
    
    
class StartTestSerializer(serializers.Serializer):
    test_id = serializers.IntegerField()

    def validate_test_id(self, value):
        try:
            test = Test.objects.get(id=value)
        except Test.DoesNotExist:
            raise serializers.ValidationError("Test does not exist.")

        if test.status != "PUBLISHED":
            raise serializers.ValidationError("Test is not published yet.")

        self.test = test
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        test = self.test

        # Create TestAttempt
        attempt = TestAttempt.objects.create(user=user, test=test)

        # For each category in test, pick questions
        category_configs = test.category_configs.all()
        for config in category_configs:
            questions = list(config.category.category_questions.all())
            # Randomly select required number
            import random
            selected_questions = random.sample(
                questions, min(len(questions), config.number_of_questions)
            )

            # Create AttemptCategory
            attempt_category = AttemptCategory.objects.create(
                attempt=attempt,
                category=config.category
            )
            attempt_category.question_set.set(selected_questions)

        return attempt
    
    
class AttemptCategoryQuestionSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    questions = serializers.SerializerMethodField()

    class Meta:
        model = AttemptCategory
        fields = ["id", "category", "category_name", "questions"]

    def get_category_name(self, obj):
        # Make sure obj.category is the FK to QuestionCategory
        return obj.category.name if obj.category else None

    def get_questions(self, obj):
        # Make sure you are using the correct related_name for questions
        # e.g., if TestQuestion model has FK AttemptCategory with related_name='questions':
        questions = obj.question_set.all()  # replace with correct related_name
        return QuestionSerializer(questions, many=True).data


    
    
class SubmitAnswerSerializer(serializers.ModelSerializer):
    attempt = serializers.PrimaryKeyRelatedField(queryset=TestAttempt.objects.all())
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())
    
    class Meta:
        model = UserAnswer
        fields = ["attempt", "question", "selected_option"]

    def validate(self, attrs):
        attempt = attrs.get("attempt")
        question = attrs.get("question")
        user = self.context["request"].user

        # Check attempt belongs to user
        if attempt.user != user:
            raise serializers.ValidationError("This attempt does not belong to you.")

        # Check question belongs to attempt
        attempt_questions = attempt.categories.values_list("question_set", flat=True)
        if question.id not in attempt_questions:
            raise serializers.ValidationError("Question does not belong to this test attempt.")

        return attrs

    def create(self, validated_data):
        question = validated_data["question"]
        attempt = validated_data["attempt"]
        selected_option = validated_data["selected_option"]

        # Check correctness
        is_correct = question.correct_option == selected_option

        # Create or update UserAnswer
        user_answer, created = UserAnswer.objects.update_or_create(
            attempt=attempt,
            question=question,
            defaults={"selected_option": selected_option, "is_correct": is_correct},
        )
        return user_answer
    
    
from django.utils import timezone

class SubmitTestSerializer(serializers.Serializer):
    attempt_id = serializers.IntegerField()

    def validate_attempt_id(self, value):
        attempt = TestAttempt.objects.get(
            id=value,
            user=self.context["request"].user
        )

        if attempt.status == "COMPLETED":
            raise serializers.ValidationError("Test already submitted.")

        # 🔴 ADD THIS
        if attempt.is_time_over():
            attempt.status = "COMPLETED"
            attempt.completed_at = timezone.now()
            attempt.save()
            raise serializers.ValidationError("Test time is over.")

        self.attempt = attempt
        return value
    
    def save(self, **kwargs):
     attempt = self.attempt

     answers = attempt.answers.select_related("question")
     score = sum(
        ans.question.marks
        for ans in answers
        if ans.is_correct
    )

     attempt.score = score
     attempt.status = "COMPLETED"
     attempt.completed_at = timezone.now()
     attempt.save()

     return attempt


    

class UserAnswerResultSerializer(serializers.ModelSerializer):
    selected_option = serializers.SerializerMethodField()
    is_correct = serializers.SerializerMethodField()
    options = serializers.SerializerMethodField()
    attempted = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            "id",
            "question_text",
            "options",
            "selected_option",
            "correct_option",
            "is_correct",
            "answer_explanation",
            "attempted",
        ]

    def _get_answer(self, obj):
        attempt = self.context.get("attempt")
        if not attempt:
            return None
        return attempt.answers.filter(question=obj).first()

    def get_selected_option(self, obj):
        answer = self._get_answer(obj)
        return answer.selected_option if answer else None

    def get_is_correct(self, obj):
        answer = self._get_answer(obj)
        return bool(answer and answer.selected_option == obj.correct_option)

    def get_attempted(self, obj):
        return self._get_answer(obj) is not None

    def get_options(self, obj):
        return {
            "A": obj.option_a,
            "B": obj.option_b,
            "C": obj.option_c,
            "D": obj.option_d,
        }


class CategoryResultSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name")
    questions = serializers.SerializerMethodField()
    category_score = serializers.SerializerMethodField()

    class Meta:
        model = AttemptCategory
        fields = ["category_name", "category_score", "questions"]

    def get_questions(self, obj):
        questions = obj.question_set.all().distinct()

        serializer = UserAnswerResultSerializer(
            questions,
            many=True,
            context={"attempt": obj.attempt}
        )
        return serializer.data

    def get_category_score(self, obj):
        return sum(
            1
            for question in obj.question_set.all().distinct()
            if obj.attempt.answers.filter(
                question=question,
                selected_option=question.correct_option
            ).exists()
        )




class TestResultSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()
    max_score = serializers.SerializerMethodField()
    percentage = serializers.SerializerMethodField()
    passed = serializers.SerializerMethodField()
    time_taken = serializers.SerializerMethodField()

    class Meta:
        model = TestAttempt
        fields = [
            "id",
            "test",
            "score",
            "max_score",
            "status",
            "percentage",
            "passed",
            "categories",
            "time_taken",
        ]

    def get_categories(self, obj):
        seen = set()
        unique_categories = []

        for cat in obj.categories.select_related("category").prefetch_related("question_set"):
            if cat.category_id not in seen:
                seen.add(cat.category_id)
                unique_categories.append(cat)

        serializer = CategoryResultSerializer(unique_categories, many=True)
        return serializer.data

    def get_max_score(self, obj):
        return sum(
            category.question_set.all().distinct().count()
            for category in obj.categories.all()
        )

    def get_percentage(self, obj):
        max_score = self.get_max_score(obj)
        return round((obj.score / max_score) * 100, 2) if max_score else 0

    def get_passed(self, obj):
        passing_percentage = getattr(obj.test, "passing_percentage", 40)
        return self.get_percentage(obj) >= passing_percentage

    def get_time_taken(self, obj):
        if not obj.completed_at:
            return None
        delta = obj.completed_at - obj.started_at
        minutes, seconds = divmod(int(delta.total_seconds()), 60)
        return f"{minutes} min {seconds} sec"

    
    


class AdminTestResultSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username")
    test_name = serializers.CharField(source="test.name")
    max_score = serializers.SerializerMethodField()
    percentage = serializers.SerializerMethodField()
    passed = serializers.SerializerMethodField()
    time_taken = serializers.SerializerMethodField()

    class Meta:
        model = TestAttempt
        fields = [
            "id",
            "user",
            "test_name",
            "score",
            "max_score",
            "percentage",
            "status",
            "passed",
            "time_taken",
            "started_at",
            "completed_at",
        ]

    def get_max_score(self, obj):
        return sum(category.question_set.count() for category in obj.categories.all())

    def get_percentage(self, obj):
        max_score = self.get_max_score(obj)
        return round((obj.score / max_score) * 100, 2) if max_score else 0

    def get_passed(self, obj):
        return obj.calculate_pass_fail()["passed"]

    def get_time_taken(self, obj):
        if not obj.completed_at:
            return None
        total_seconds = int((obj.completed_at - obj.started_at).total_seconds())
        minutes, seconds = divmod(total_seconds, 60)
        return f"{minutes} min {seconds} sec"

    
    














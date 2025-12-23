from django.db import models
from accounts.models import User
from django.utils import timezone
from datetime import timedelta

class Test(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    duration = models.PositiveIntegerField(help_text="Minutes")
    max_questions = models.PositiveIntegerField()

    total_marks = models.PositiveIntegerField()
    passing_marks = models.PositiveIntegerField()

    status = models.CharField(
        max_length=10,
        choices=[("DRAFT", "Draft"), ("PUBLISHED", "Published")],
        default="DRAFT",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    
    
class QuestionCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
    
class TestCategoryConfig(models.Model):
    test = models.ForeignKey(
        Test,
        related_name="category_configs",
        on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        QuestionCategory,
        on_delete=models.CASCADE
    )
    number_of_questions = models.PositiveIntegerField()

    class Meta:
        unique_together = ("test", "category")


    def __str__(self):
        return f"{self.test.name} - {self.category.name} ({self.number_of_questions})"


    
class Question(models.Model):
    question_category = models.ForeignKey(
        QuestionCategory, 
        related_name="category_questions",
        on_delete=models.SET_NULL,
        null=True
    )
    question_text = models.TextField()  # rich text if needed
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(
        max_length=1,
        choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")]
    )
    marks = models.PositiveIntegerField(default=1)
    answer_explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.question_text[:50]
    
    
class TestAttempt(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="test_attempts"
    )
    test = models.ForeignKey(
        "tests.Test",
        on_delete=models.CASCADE,
        related_name="attempts"
    )
    score = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=10,
        choices=[("ONGOING", "Ongoing"), ("COMPLETED", "Completed")],
        default="ONGOING"
    )

    def __str__(self):
        return f"{self.user.username} - {self.test.name} ({self.status})"

    # 🔹 Check if test time is over
    def is_time_over(self):
        end_time = self.started_at + timedelta(minutes=self.test.duration)
        return timezone.now() >= end_time

    # 🔹 Remaining seconds (for frontend timer)
    def time_left(self):
      if self.status == "COMPLETED":
            return "00 min 00 sec"

      end_time = self.started_at + timedelta(minutes=self.test.duration)
      remaining = end_time - timezone.now()

      if remaining.total_seconds() <= 0:
            return "00 min 00 sec"

      minutes, seconds = divmod(int(remaining.total_seconds()), 60)
      return f"{minutes} min {seconds} sec"


    # 🔹 Pass / Fail logic
    def calculate_pass_fail(self):
        total_marks = sum(q.marks for q in self.test.questions.all())
        passing_percentage = getattr(self.test, "passing_percentage", 50)
        passing_marks = (passing_percentage / 100) * total_marks

        passed = self.score >= passing_marks
        return {
            "passed": passed,
            "status": "PASS" if passed else "FAIL"
        }

    
    
class AttemptCategory(models.Model):
    attempt = models.ForeignKey(TestAttempt, on_delete=models.CASCADE, related_name="categories")
    category = models.ForeignKey("tests.QuestionCategory", on_delete=models.CASCADE)
    question_set = models.ManyToManyField("tests.Question", blank=True)
    completed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ("attempt", "category")

    def __str__(self):
        return f"{self.attempt} - {self.category.name}"


class UserAnswer(models.Model):
    attempt = models.ForeignKey(TestAttempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1, choices=[('A','A'),('B','B'),('C','C'),('D','D')])
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.attempt.user.username} - Q{self.question.id} - {self.selected_option}"







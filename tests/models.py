from django.db import models

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
    category = models.ForeignKey(
        QuestionCategory,
        related_name="questions",
        on_delete=models.CASCADE
    )

    question_text = models.TextField()

    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)

    correct_option = models.CharField(
        max_length=1,
        choices=[('A','A'), ('B','B'), ('C','C'), ('D','D')]
    )

    marks = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.question_text[:50]





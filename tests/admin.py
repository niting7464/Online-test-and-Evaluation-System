from django.contrib import admin
from .models import Test, QuestionCategory, TestCategoryConfig, Question


admin.site.register(Test)
admin.site.register(TestCategoryConfig)

if admin.site.is_registered(QuestionCategory):
    admin.site.unregister(QuestionCategory)

@admin.register(QuestionCategory)
class QuestionCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "question_text", "question_category")
    list_filter = ("question_category",)
    search_fields = ("question_text",)

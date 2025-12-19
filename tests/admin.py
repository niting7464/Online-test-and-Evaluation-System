from django.contrib import admin
from .models import Test, QuestionCategory, TestCategoryConfig


admin.site.register(Test)
admin.site.register(QuestionCategory)
admin.site.register(TestCategoryConfig)

import json
from django.core.management.base import BaseCommand
from tests.models import QuestionCategory, Question, Test, TestCategoryConfig

class Command(BaseCommand):
    help = "Import sample tests from JSON"

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help="Path to JSON file")

    def handle(self, *args, **options):
        file_path = options['json_file']
        self.stdout.write(f"Importing from {file_path}...")

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 1️⃣ Categories
        categories_map = {}
        for cat_data in data.get('categories', []):
            cat, created = QuestionCategory.objects.get_or_create(
                name=cat_data['name']
            )
            categories_map[cat.name] = cat
            if created:
                self.stdout.write(f"Created category: {cat.name}")

        # 2️⃣ Questions
        for q_data in data.get('questions', []):
            cat_name = q_data['question_category']
            category = categories_map.get(cat_name)
            if not category:
                self.stdout.write(self.style.WARNING(f"Skipping question, unknown category: {cat_name}"))
                continue

            question, created = Question.objects.get_or_create(
                question_text=q_data['question_text'],
                question_category=category,
                defaults={
                    'option_a': q_data['option_a'],
                    'option_b': q_data['option_b'],
                    'option_c': q_data['option_c'],
                    'option_d': q_data['option_d'],
                    'correct_option': q_data['correct_option'],
                    'marks': q_data.get('marks', 1),
                    'answer_explanation': q_data.get('answer_explanation', '')
                }
            )
            if created:
                self.stdout.write(f"Created question: {question.question_text[:50]}")

        # 3️⃣ Tests
        tests_map = {}
        for t_data in data.get('tests', []):
            test, created = Test.objects.get_or_create(
                name=t_data['name'],
                defaults={
                    'description': t_data.get('description', ''),
                    'duration': t_data.get('duration', 15),
                    'max_questions': t_data.get('max_questions', 10),
                    'total_marks': t_data.get('total_marks', 10),
                    'passing_marks': t_data.get('passing_marks', 5),
                    'status': t_data.get('status', 'DRAFT')
                }
            )
            tests_map[test.name] = test
            if created:
                self.stdout.write(f"Created test: {test.name}")

        # 4️⃣ TestCategoryConfig
        for cfg in data.get('test_category_configs', []):
            test = tests_map.get(cfg['test'])
            category = categories_map.get(cfg['category'])
            if not test or not category:
                self.stdout.write(self.style.WARNING(f"Skipping config: {cfg}"))
                continue

            config, created = TestCategoryConfig.objects.get_or_create(
                test=test,
                category=category,
                defaults={'number_of_questions': cfg['number_of_questions']}
            )
            if created:
                self.stdout.write(f"Added category config: {test.name} - {category.name} ({config.number_of_questions})")

        self.stdout.write(self.style.SUCCESS("Import completed!"))

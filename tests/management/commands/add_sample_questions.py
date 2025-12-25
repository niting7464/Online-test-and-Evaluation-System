from django.core.management.base import BaseCommand
from tests.models import QuestionCategory, Question


class Command(BaseCommand):
    help = 'Adds sample questions to each category'

    def handle(self, *args, **options):
        # Sample questions for different categories
        sample_questions = {
            'Mathematics': [
                {
                    'question_text': 'What is 2 + 2?',
                    'option_a': '3',
                    'option_b': '4',
                    'option_c': '5',
                    'option_d': '6',
                    'correct_option': 'B',
                    'marks': 1,
                    'answer_explanation': 'Basic addition: 2 + 2 = 4'
                },
                {
                    'question_text': 'What is the square root of 16?',
                    'option_a': '2',
                    'option_b': '3',
                    'option_c': '4',
                    'option_d': '5',
                    'correct_option': 'C',
                    'marks': 1,
                    'answer_explanation': 'The square root of 16 is 4 because 4 × 4 = 16'
                },
                {
                    'question_text': 'What is 10 × 5?',
                    'option_a': '40',
                    'option_b': '45',
                    'option_c': '50',
                    'option_d': '55',
                    'correct_option': 'C',
                    'marks': 1,
                    'answer_explanation': '10 multiplied by 5 equals 50'
                },
                {
                    'question_text': 'What is the value of π (pi) approximately?',
                    'option_a': '2.14',
                    'option_b': '3.14',
                    'option_c': '4.14',
                    'option_d': '5.14',
                    'correct_option': 'B',
                    'marks': 1,
                    'answer_explanation': 'Pi (π) is approximately 3.14159...'
                },
                {
                    'question_text': 'What is 15 ÷ 3?',
                    'option_a': '3',
                    'option_b': '4',
                    'option_c': '5',
                    'option_d': '6',
                    'correct_option': 'C',
                    'marks': 1,
                    'answer_explanation': '15 divided by 3 equals 5'
                }
            ],
            'Science': [
                {
                    'question_text': 'What is the chemical symbol for water?',
                    'option_a': 'H2O',
                    'option_b': 'CO2',
                    'option_c': 'O2',
                    'option_d': 'NaCl',
                    'correct_option': 'A',
                    'marks': 1,
                    'answer_explanation': 'Water is composed of two hydrogen atoms and one oxygen atom, hence H2O'
                },
                {
                    'question_text': 'What planet is known as the Red Planet?',
                    'option_a': 'Venus',
                    'option_b': 'Mars',
                    'option_c': 'Jupiter',
                    'option_d': 'Saturn',
                    'correct_option': 'B',
                    'marks': 1,
                    'answer_explanation': 'Mars is called the Red Planet due to iron oxide (rust) on its surface'
                },
                {
                    'question_text': 'What is the speed of light in vacuum?',
                    'option_a': '300,000 km/s',
                    'option_b': '150,000 km/s',
                    'option_c': '450,000 km/s',
                    'option_d': '600,000 km/s',
                    'correct_option': 'A',
                    'marks': 1,
                    'answer_explanation': 'The speed of light in vacuum is approximately 299,792,458 m/s or about 300,000 km/s'
                },
                {
                    'question_text': 'What is the largest organ in the human body?',
                    'option_a': 'Liver',
                    'option_b': 'Lungs',
                    'option_c': 'Skin',
                    'option_d': 'Heart',
                    'correct_option': 'C',
                    'marks': 1,
                    'answer_explanation': 'The skin is the largest organ, covering the entire body'
                },
                {
                    'question_text': 'What gas do plants absorb from the atmosphere?',
                    'option_a': 'Oxygen',
                    'option_b': 'Nitrogen',
                    'option_c': 'Carbon Dioxide',
                    'option_d': 'Hydrogen',
                    'correct_option': 'C',
                    'marks': 1,
                    'answer_explanation': 'Plants absorb carbon dioxide (CO2) during photosynthesis'
                }
            ],
            'General Knowledge': [
                {
                    'question_text': 'What is the capital of France?',
                    'option_a': 'London',
                    'option_b': 'Berlin',
                    'option_c': 'Paris',
                    'option_d': 'Madrid',
                    'correct_option': 'C',
                    'marks': 1,
                    'answer_explanation': 'Paris is the capital and largest city of France'
                },
                {
                    'question_text': 'Who wrote "Romeo and Juliet"?',
                    'option_a': 'Charles Dickens',
                    'option_b': 'William Shakespeare',
                    'option_c': 'Jane Austen',
                    'option_d': 'Mark Twain',
                    'correct_option': 'B',
                    'marks': 1,
                    'answer_explanation': 'Romeo and Juliet is a tragedy written by William Shakespeare'
                },
                {
                    'question_text': 'What is the largest ocean on Earth?',
                    'option_a': 'Atlantic Ocean',
                    'option_b': 'Indian Ocean',
                    'option_c': 'Arctic Ocean',
                    'option_d': 'Pacific Ocean',
                    'correct_option': 'D',
                    'marks': 1,
                    'answer_explanation': 'The Pacific Ocean is the largest and deepest ocean on Earth'
                },
                {
                    'question_text': 'In which year did World War II end?',
                    'option_a': '1943',
                    'option_b': '1944',
                    'option_c': '1945',
                    'option_d': '1946',
                    'correct_option': 'C',
                    'marks': 1,
                    'answer_explanation': 'World War II ended in 1945'
                },
                {
                    'question_text': 'What is the smallest prime number?',
                    'option_a': '0',
                    'option_b': '1',
                    'option_c': '2',
                    'option_d': '3',
                    'correct_option': 'C',
                    'marks': 1,
                    'answer_explanation': '2 is the smallest and only even prime number'
                }
            ],
            'Programming': [
                {
                    'question_text': 'What does HTML stand for?',
                    'option_a': 'HyperText Markup Language',
                    'option_b': 'High-level Text Markup Language',
                    'option_c': 'HyperText Machine Language',
                    'option_d': 'Home Tool Markup Language',
                    'correct_option': 'A',
                    'marks': 1,
                    'answer_explanation': 'HTML stands for HyperText Markup Language, used for creating web pages'
                },
                {
                    'question_text': 'Which programming language is known as the "language of the web"?',
                    'option_a': 'Python',
                    'option_b': 'Java',
                    'option_c': 'JavaScript',
                    'option_d': 'C++',
                    'correct_option': 'C',
                    'marks': 1,
                    'answer_explanation': 'JavaScript is the primary programming language for web development'
                },
                {
                    'question_text': 'What is the output of: print(2 + 3 * 4) in Python?',
                    'option_a': '20',
                    'option_b': '14',
                    'option_c': '11',
                    'option_d': '24',
                    'correct_option': 'B',
                    'marks': 1,
                    'answer_explanation': 'Order of operations: 3 * 4 = 12, then 2 + 12 = 14'
                },
                {
                    'question_text': 'What does CSS stand for?',
                    'option_a': 'Computer Style Sheets',
                    'option_b': 'Cascading Style Sheets',
                    'option_c': 'Creative Style Sheets',
                    'option_d': 'Colorful Style Sheets',
                    'correct_option': 'B',
                    'marks': 1,
                    'answer_explanation': 'CSS stands for Cascading Style Sheets, used for styling web pages'
                },
                {
                    'question_text': 'Which data structure follows LIFO (Last In First Out) principle?',
                    'option_a': 'Queue',
                    'option_b': 'Stack',
                    'option_c': 'Array',
                    'option_d': 'Linked List',
                    'correct_option': 'B',
                    'marks': 1,
                    'answer_explanation': 'Stack follows LIFO principle where the last element added is the first one removed'
                }
            ]
        }

        created_count = 0
        updated_count = 0

        # Get or create categories and add questions
        for category_name, questions in sample_questions.items():
            category, created = QuestionCategory.objects.get_or_create(name=category_name)
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category_name}'))
            else:
                self.stdout.write(f'Using existing category: {category_name}')

            for q_data in questions:
                question, created = Question.objects.get_or_create(
                    question_text=q_data['question_text'],
                    question_category=category,
                    defaults={
                        'option_a': q_data['option_a'],
                        'option_b': q_data['option_b'],
                        'option_c': q_data['option_c'],
                        'option_d': q_data['option_d'],
                        'correct_option': q_data['correct_option'],
                        'marks': q_data['marks'],
                        'answer_explanation': q_data.get('answer_explanation', ''),
                        'is_active': True
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f'  Created question: {q_data["question_text"][:50]}...')
                else:
                    updated_count += 1
                    # Update existing question
                    question.option_a = q_data['option_a']
                    question.option_b = q_data['option_b']
                    question.option_c = q_data['option_c']
                    question.option_d = q_data['option_d']
                    question.correct_option = q_data['correct_option']
                    question.marks = q_data['marks']
                    question.answer_explanation = q_data.get('answer_explanation', '')
                    question.is_active = True
                    question.save()
                    self.stdout.write(f'  Updated question: {q_data["question_text"][:50]}...')

        self.stdout.write(self.style.SUCCESS(
            f'\nSuccessfully processed {created_count} new questions and {updated_count} updated questions'
        ))


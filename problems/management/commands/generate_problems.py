import random
from django.core.management.base import BaseCommand
from problems.models import Problem, Solution, Hint, Deck, DeckTagFilter, BookSource
from taggit.models import Tag

class Command(BaseCommand):
    help = 'Generates sample problems, solutions, hints, tags, and decks.'

    def handle(self, *args, **options):
        # Clean up old data to prevent duplicates
        self.stdout.write('Cleaning old data...')
        Problem.objects.all().delete()
        BookSource.objects.all().delete()
        Solution.objects.all().delete()
        Hint.objects.all().delete()
        Deck.objects.all().delete()
        DeckTagFilter.objects.all().delete()
        Tag.objects.all().delete() # Must be last if tags are used in other models

        self.stdout.write('Creating new data...')

        # 1. Create Tags
        subjects = ['Algebra', 'Calculus', 'Geometry']
        difficulties = ['Easy', 'Medium', 'Hard']
        problem_types = ['Proof', 'Calculation', 'Theory']
        
        for tag_list in [subjects, difficulties, problem_types]:
            for tag_name in tag_list:
                Tag.objects.create(name=tag_name)
        self.stdout.write(f'  - Created {Tag.objects.count()} tags.')

        # Sample LaTeX expressions for problem bodies
        latex_expressions = [
            r"Solve for \(x\): \(ax^2 + bx + c = 0\). The solution is given by the quadratic formula: \[x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}\]",
            r"What is the value of the integral \(\int_{0}^{\infty} e^{-x^2} dx\)? This is the Gaussian integral, and its value is \(\frac{\sqrt{\pi}}{2}\).",
            r"Prove Euler's identity: \(e^{i\pi} + 1 = 0\). This beautiful equation connects five fundamental mathematical constants.",
            r"Find the derivative of \(f(x) = \sin(x^2)\). Using the chain rule, we get \(f'(x) = \cos(x^2) \cdot 2x\).",
            r"What is the statement of the Pythagorean theorem? For a right-angled triangle with sides a, b, and hypotenuse c, it is \(a^2 + b^2 = c^2\).",
            r"Calculate the limit: \(\lim_{x \to 0} \frac{\sin(x)}{x}\). This fundamental limit in calculus is equal to 1.",
            r"The Fourier Transform of a function \(f(t)\) is given by \[\hat{f}(\omega) = \int_{-\infty}^{\infty} f(t) e^{-i\omega t} dt\]"
        ]
        
        # Pre-generate some book sources
        book_sources = [
            BookSource.objects.create(title="Calculus: Early Transcendentals", author="James Stewart"),
            BookSource.objects.create(title="Linear Algebra and Its Applications", author="David C. Lay"),
            BookSource.objects.create(title="Principles of Mathematical Analysis", author="Walter Rudin"),
        ]
        self.stdout.write(f'  - Created {len(book_sources)} book sources.')
        
        # 2. Create Problems
        num_problems = 50
        for i in range(num_problems):
            subject = random.choice(subjects)
            difficulty = random.choice(difficulties)
            problem_type = random.choice(problem_types)
            
            # Randomly assign a book source and details
            problem_data = {
                'body': f"This is the body for a {difficulty} {subject} {problem_type} problem.\n\n{random.choice(latex_expressions)}"
            }
            if random.random() > 0.3: # 70% chance to have a book source
                problem_data['book_source'] = random.choice(book_sources)
                problem_data['page_number'] = random.randint(20, 500)
                problem_data['problem_number'] = f"{random.randint(1, 15)}-{random.randint(1, 10)}"

            problem = Problem.objects.create(
                **problem_data
            )
            problem.tags.add(subject, difficulty, problem_type)

            # Create 1 to 3 hints for each problem
            for j in range(random.randint(1, 3)):
                Hint.objects.create(problem=problem, body=f"This is hint #{j+1} for problem #{problem.pk}.")
            # Create 1 or 2 solutions for each problem
            for j in range(random.randint(1, 2)):
                Solution.objects.create(problem=problem, body=f"This is a detailed solution ({j+1}) for problem #{problem.pk}.")

        self.stdout.write(f'  - Created {num_problems} problems.')

        # 3. Create Decks
        deck_configs = [
            {'name': 'Easy Calculus', 'include': ['Easy', 'Calculus'], 'exclude': ['Geometry']},
            {'name': 'Hard Problems', 'include': ['Hard'], 'exclude': []},
            {'name': 'All except Algebra', 'include': [], 'exclude': ['Algebra']},
        ]

        for config in deck_configs:
            deck = Deck.objects.create(name=config['name'])
            for tag_name in config['include']:
                tag = Tag.objects.get(name=tag_name)
                DeckTagFilter.objects.create(deck=deck, tag=tag, filter_type=DeckTagFilter.FilterType.INCLUDE)
            for tag_name in config['exclude']:
                tag = Tag.objects.get(name=tag_name)
                DeckTagFilter.objects.create(deck=deck, tag=tag, filter_type=DeckTagFilter.FilterType.EXCLUDE)
            
            self.stdout.write(f"  - Created Deck '{deck.name}'")
            problems = deck.problems
            self.stdout.write(f"    Problems in deck ({problems.count()}):")
            for problem in problems[:3]: # Show a few examples
                self.stdout.write(f"    - Problem #{problem.pk} (Tags: {', '.join(t.name for t in problem.tags.all())})")
            if problems.count() > 3:
                self.stdout.write(f"    - ... and {problems.count() - 3} more.")

        self.stdout.write(self.style.SUCCESS('Successfully generated sample data.'))

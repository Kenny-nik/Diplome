# apps/books/management/commands/create_demo_books.py
import random
from django.core.management.base import BaseCommand
from apps.books.models import Book

TITLES = [
    "The Silent Library", "Quantum Dreams", "Lost in Pages", "History of Us",
    "Ocean of Stars", "Romance in Paris", "Mystery of Dawn", "Tech Rebels",
    "Python Cookbook", "Data Voyager", "AI for Humans", "Deep Forest",
    "Time Travelers", "Edge of Science", "Hidden Figures", "Love & Letters",
    "Ancient Worlds", "Zero to One More", "Clean Architecture Notes", "Cosmic Tales",
    "City of Books", "The Last Algorithm", "Practical Django", "Chronicles of Code",
    "Philosophy for Devs",
]
AUTHORS = ["A. Smith", "B. Johnson", "C. Williams", "D. Brown", "E. Davis", "F. Wilson"]
GENRES = ["FICTION", "SCI_FI", "MYSTERY", "ROMANCE", "HISTORY", "SCIENCE", "TECH"]

class Command(BaseCommand):
    """
    Создаёт/обновляет 20 демо-книг.
    ВАЖНО: cover_url теперь пустой -> в шаблонах всегда берём локальные обложки по жанру.
    """
    help = "Create or update 20 demo books with static (local) covers by genre."

    def handle(self, *args, **options):
        created = 0
        updated = 0
        for i, title in enumerate(TITLES[:20], start=1):
            isbn = f"DEMO-{i:05d}"
            genre = random.choice(GENRES)
            defaults = {
                "title": f"[DEMO] {title}",
                "author": random.choice(AUTHORS),
                "publication_year": random.randint(1995, 2024),
                "genre": genre,
                "description": "Demo book for UI preview.",
                "cover_url": "",                                 # <- статичные локальные обложки
                "rating": round(random.uniform(3.0, 5.0), 2),
                "total_copies": random.randint(1, 5),
                "available_copies": random.randint(0, 5),
                "is_available": True,
            }
            obj, was_created = Book.objects.get_or_create(isbn=isbn, defaults=defaults)
            if was_created:
                created += 1
            else:
                # перезаписываем, чтобы очистить старые cover_url
                for k, v in defaults.items():
                    setattr(obj, k, v)
                obj.save()
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"Created: {created}, updated: {updated} demo books"))

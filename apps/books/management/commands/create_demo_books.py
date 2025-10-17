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

# Цветовые схемы и подписи для обложек (placehold.co — быстро и наглядно)
# формат: background/foreground + подпись
GENRE_COVER_STYLE = {
    "FICTION":  ("fde68a/7c2d12", "Fiction"),
    "SCI_FI":   ("bde0fe/0f172a", "Sci-Fi"),
    "MYSTERY":  ("c7d2fe/111827", "Mystery"),
    "ROMANCE":  ("fecdd3/7f1d1d", "Romance"),
    "HISTORY":  ("d1fae5/064e3b", "History"),
    "SCIENCE":  ("e0e7ff/1e3a8a", "Science"),
    "TECH":     ("e5e7eb/111827", "Tech"),
}

def cover_for(genre_code: str, i: int) -> str:
    bgfg, label = GENRE_COVER_STYLE.get(genre_code, ("e5e7eb/111827", "Book"))
    # Немного разнообразия: несколько размеров и подпись с номером
    return f"https://placehold.co/320x430/{bgfg}?text={label}+#{i}"

class Command(BaseCommand):
    help = "Create or update 20 demo books with genre-based cover_url and rating."

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
                "cover_url": cover_for(genre, i),
                "rating": round(random.uniform(3.0, 5.0), 2),
                "total_copies": random.randint(1, 5),
                "available_copies": random.randint(0, 5),
                "is_available": True,
            }
            obj, was_created = Book.objects.get_or_create(isbn=isbn, defaults=defaults)
            if was_created:
                created += 1
            else:
                # Обновляем обложку/рейтинг/жанр и прочее, чтобы были новые картинки
                for k, v in defaults.items():
                    setattr(obj, k, v)
                obj.save()
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"Created: {created}, updated: {updated} demo books"))

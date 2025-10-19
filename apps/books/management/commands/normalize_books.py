from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.books.models import Book

VALID = {code for code, _ in getattr(Book, "GENRE_CHOICES", [])} or {
    "sci_fi", "romance", "history", "cs", "science", "detective", "poetry", "other"
}

GUESS_MAP = {
    "sci_fi": {"cosmic", "quantum", "tech", "space", "zero", "ancient worlds", "edge of science"},
    "romance": {"romance", "love"},
    "history": {"history", "ancient", "architecture"},
    "cs": {"python", "cookbook", "ai", "data", "quantum", "tech", "program", "code"},
    "science": {"science"},
    "detective": {"mystery", "deep forest", "lost"},
    "poetry": {"letters", "poetry"},
}

def guess_genre(title: str) -> str:
    t = (title or "").lower()
    for code, keys in GUESS_MAP.items():
        if any(k in t for k in keys):
            return code
    return "other"

class Command(BaseCommand):
    help = "Normalize/repair book genres and slugs based on current choices"

    def handle(self, *args, **kwargs):
        updated = 0
        for b in Book.objects.all():
            changed = []

            # slug
            if not getattr(b, "slug", None):
                b.slug = slugify(b.title)[:80] or None
                changed.append("slug")

            # genre
            g = (b.genre or "").strip().lower()
            if g not in VALID:
                new_g = guess_genre(b.title)
                if new_g != g:
                    b.genre = new_g
                    changed.append("genre")

            if changed:
                b.save(update_fields=changed)
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"Books normalized: {updated}"))

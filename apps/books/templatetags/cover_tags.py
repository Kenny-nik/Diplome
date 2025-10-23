import hashlib
from django import template

register = template.Library()

COVER_CHOICES = {
    "FICTION": [
        "img/genre_covers/FICTION/1.jpg",
        "img/genre_covers/FICTION/2.jpg",
        "img/genre_covers/FICTION/3.jpg",
        "img/genre_covers/FICTION/4.jpg",
        "img/genre_covers/FICTION/5.jpg",
    ],
    "SCI_FI": [
        "img/genre_covers/SCI_FI/1.jpg",
        "img/genre_covers/SCI_FI/2.jpg",
        "img/genre_covers/SCI_FI/3.jpg",
        "img/genre_covers/SCI_FI/4.jpg",
        "img/genre_covers/SCI_FI/5.jpg",
    ],
    "MYSTERY": [
        "img/genre_covers/MYSTERY/1.jpg",
        "img/genre_covers/MYSTERY/2.jpg",
        "img/genre_covers/MYSTERY/3.jpg",
        "img/genre_covers/MYSTERY/4.jpg",
        "img/genre_covers/MYSTERY/5.jpg",
    ],
    "ROMANCE": [
        "img/genre_covers/ROMANCE/1.jpg",
        "img/genre_covers/ROMANCE/2.jpg",
        "img/genre_covers/ROMANCE/3.jpg",
        "img/genre_covers/ROMANCE/4.jpg",
        "img/genre_covers/ROMANCE/5.jpg",
    ],
    "HISTORY": [
        "img/genre_covers/HISTORY/1.jpg",
        "img/genre_covers/HISTORY/2.jpg",
        "img/genre_covers/HISTORY/3.jpg",
        "img/genre_covers/HISTORY/4.jpg",
        "img/genre_covers/HISTORY/5.jpg",
    ],
    "SCIENCE": [
        "img/genre_covers/SCIENCE/1.jpg",
        "img/genre_covers/SCIENCE/2.jpg",
        "img/genre_covers/SCIENCE/3.jpg",
        "img/genre_covers/SCIENCE/4.jpg",
        "img/genre_covers/SCIENCE/5.jpg",
    ],
    "TECH": [
        "img/genre_covers/TECH/1.jpg",
        "img/genre_covers/TECH/2.jpg",
        "img/genre_covers/TECH/3.jpg",
        "img/genre_covers/TECH/4.jpg",
        "img/genre_covers/TECH/5.jpg",
    ],
}

def _stable_index(key: str, n: int) -> int:
    if not key:
        key = "fallback-key"
    digest = hashlib.md5(key.encode("utf-8")).hexdigest()
    return int(digest, 16) % n if n else 0

@register.simple_tag
def cover_for_book(book) -> str:
    """Стабильная локальная обложка для конкретной книги по её ISBN (или title+author)."""
    genre = (getattr(book, "genre", None) or "FICTION").upper()
    files = COVER_CHOICES.get(genre) or COVER_CHOICES["FICTION"]
    key = getattr(book, "isbn", None) or f"{getattr(book, 'title', '')}-{getattr(book, 'author', '')}"
    idx = _stable_index(key, len(files))
    return files[idx]

@register.simple_tag
def cover_for_genre(genre_code: str) -> str:
    """Совместимость со старыми шаблонами: даёт стабильную обложку по жанру."""
    genre = (genre_code or "FICTION").upper()
    files = COVER_CHOICES.get(genre) or COVER_CHOICES["FICTION"]
    idx = _stable_index(genre, len(files))
    return files[idx]
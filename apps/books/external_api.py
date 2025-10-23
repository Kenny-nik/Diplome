import requests
from .models import Book

class GoogleBooksAPI:
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"

    @staticmethod
    def fetch_books(query: str, max_results: int = 10):
        """Получает список книг по запросу query из Google Books API."""
        params = {"q": query, "maxResults": max_results}
        try:
            response = requests.get(GoogleBooksAPI.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Ошибка запроса к Google Books API: {e}")
            return []

        data = response.json()
        books = []
        for item in data.get("items", []):
            info = item.get("volumeInfo", {})
            books.append({
                "title": info.get("title"),
                "authors": ", ".join(info.get("authors", [])),
                "published_date": info.get("publishedDate"),
                "description": info.get("description"),
                "thumbnail": info.get("imageLinks", {}).get("thumbnail"),
                "info_link": info.get("infoLink"),
            })
        return books

    @staticmethod
    def save_books_to_db(books_data):
        """Сохраняет книги в локальную таблицу Book, если они еще не существуют."""
        for data in books_data:
            if not Book.objects.filter(title=data["title"], author=data["authors"]).exists():
                Book.objects.create(
                    title=data["title"],
                    author=data["authors"],
                    published_date=data.get("published_date"),
                    description=data.get("description"),
                    thumbnail=data.get("thumbnail"),
                    info_link=data.get("info_link")
                )

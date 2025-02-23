import json

from fastapi import status
from fastapi.testclient import TestClient

from schemas.book import Book, BooksWithGenres


def test_create_book(test_app: TestClient) -> None:
    """Test that book with genre <> 'horror' can be created."""
    # Arrange
    book = {
        "title": "Fifty Shades of Grey 4",
        "author": "E.L. James",
        "publication_year": 1599,
        "genre": "18+",
    }

    # Act
    response = test_app.post("/api/v1/books", json=book)

    # Assert
    assert response.status_code == status.HTTP_201_CREATED


def test_create_horror_book(test_app: TestClient) -> None:
    """Test that book with genre == 'horror' can't be created."""
    # Arrange
    book = {
        "title": "Fifty Shades of Grey 4",
        "author": "E.L. James",
        "publication_year": 1599,
        "genre": "horror",
    }

    # Act
    response = test_app.post("/api/v1/books", json=book)

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.text == '{"reason":"Books with genre horror cannot be added."}'


def test_get_all_books(test_app: TestClient) -> None:
    """
    Test get books endpoint.

    Check that get books:
    - returns books grouped by genre and with count of books in that genre.
    - returns censored titles for genre 18+.
    """
    # Arrange
    book = {
        "title": "Fifty Shades of Grey 4",
        "author": "E.L. James",
        "publication_year": 1599,
        "genre": "18+",
    }
    test_app.post("/api/v1/books", json=book)
    book = {
        "title": "Fifty Shades of Grey 2",
        "author": "E.L. James",
        "publication_year": 1599,
        "genre": "18+",
    }
    test_app.post("/api/v1/books", json=book)
    book = {
        "title": "Fifty Shades of Grey 4",
        "author": "E.L. James",
        "publication_year": 1599,
        "genre": "drama",
    }
    test_app.post("/api/v1/books", json=book)

    # Act
    response = test_app.get("/api/v1/books")
    assert response.status_code == status.HTTP_200_OK

    response = json.loads(response.content)
    response = [BooksWithGenres(**item) for item in response.get("items")]

    # Assert
    assert len(response) == 2

    assert response[0].count == 2
    assert response[0].genre == "18+"
    assert response[0].books[0].title == response[0].books[1].title == "CENSORED"

    assert response[1].count == 1
    assert response[1].books[0].title == "Fifty Shades of Grey 4"


def test_get_all_books_no_books(test_app: TestClient) -> None:
    """Test get books endpoint when no books exist."""
    # Act
    response = test_app.get("/api/v1/books")

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.text == '{"reason":"No books in the library. Sorry!"}'


def test_update_books(test_app: TestClient) -> None:
    """Test update books endpoint when all books from the payload exist."""
    # Arrange
    book_1 = {
        "title": "Fifty Shades of Grey 4",
        "author": "E.L. James",
        "publication_year": 1599,
        "genre": "drama",
    }
    test_app.post("/api/v1/books", json=book_1)
    book_2 = {
        "title": "Fifty Shades of Grey 3",
        "author": "E.L. James",
        "publication_year": 1599,
        "genre": "drama",
    }
    test_app.post("/api/v1/books", json=book_2)

    book_1["id"] = 1
    book_1["title"] = "NEW"
    book_2["id"] = 2
    book_2["author"] = "NEW"

    # Act
    response = test_app.put("/api/v1/books", json=[book_1, book_2])
    assert response.status_code == status.HTTP_200_OK

    response = json.loads(response.content)
    response = [Book(**item) for item in response]

    # Assert
    assert len(response) == 2

    assert response[0].title == "NEW"
    assert response[1].author == "NEW"


def test_update_books_only_one_exists(test_app: TestClient) -> None:
    """Test update books endpoint when not all books from the payload exist."""
    # Arrange
    book_1 = {
        "title": "Fifty Shades of Grey 4",
        "author": "E.L. James",
        "publication_year": 1599,
        "genre": "drama",
    }
    test_app.post("/api/v1/books", json=book_1)
    book_2 = {
        "title": "Fifty Shades of Grey 3",
        "author": "E.L. James",
        "publication_year": 1599,
        "genre": "drama",
    }

    book_1["id"] = 1
    book_1["title"] = "NEW"
    book_2["id"] = 2
    book_2["author"] = "NEW"

    # Act
    response = test_app.put("/api/v1/books", json=[book_1, book_2])

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.text == '{"reason":"Not all books found. Update is allowed only for existing books."}'


def test_delete_book(test_app: TestClient) -> None:
    """Test delete book endpoint when the book is not the last book of a genre."""
    # Arrange
    book = {
        "title": "Fifty Shades of Grey 4",
        "author": "E.L. James",
        "publication_year": 1599,
        "genre": "18+",
    }
    test_app.post("/api/v1/books", json=book)
    book = {
        "title": "Fifty Shades of Grey 7",
        "author": "E.L. James",
        "publication_year": 1599,
        "genre": "18+",
    }
    test_app.post("/api/v1/books", json=book)

    # Act
    response = test_app.delete("/api/v1/books/1")
    assert response.status_code == status.HTTP_200_OK

    # Assert
    response = test_app.get("/api/v1/books")
    response = json.loads(response.content)
    response = [BooksWithGenres(**item) for item in response.get("items")]

    assert len(response) == 1

    assert response[0].count == 1


def test_delete_last_genre_book(test_app: TestClient) -> None:
    """Test delete book endpoint when the book is the last book of a genre."""
    # Arrange
    book = {
        "title": "Fifty Shades of Grey 4",
        "author": "E.L. James",
        "publication_year": 1599,
        "genre": "18+",
    }
    test_app.post("/api/v1/books", json=book)

    # Act
    response = test_app.delete("/api/v1/books/1")

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.text == '{"reason":"Cannnot delete the last book from the genre 18+."}'


def test_delete_book_does_not_exist(test_app: TestClient) -> None:
    """Test delete book endpoint when book does not exist."""
    # Act
    response = test_app.delete("/api/v1/books/1")

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.text == '{"reason":"Book with ID 1 not found."}'


def test_search_two_books_author(test_app: TestClient) -> None:
    """Test that search book endpoint returns 2 books when searched by author."""
    # Arrange
    book = {
        "title": "Fifty Shades of Grey 4",
        "author": "E.L. James",
        "publication_year": 1599,
        "genre": "drama",
    }
    test_app.post("/api/v1/books", json=book)
    book = {
        "title": "Forty Shades of Grey 7",
        "author": "E.L. James",
        "publication_year": 1599,
        "genre": "drama",
    }
    test_app.post("/api/v1/books", json=book)

    # Act
    response = test_app.get("/api/v1/books/search?author=james")

    # Assert
    assert response.status_code == status.HTTP_200_OK

    response = json.loads(response.content)
    response = [Book(**item) for item in response.get("items")]
    assert len(response) == 2


def test_search_one_book_author(test_app: TestClient) -> None:
    """Test that search book endpoint returns 1 book when searched by title."""
    # Arrange
    book = {
        "title": "Fifty Shades of Grey 4",
        "author": "E.L. James",
        "publication_year": 1599,
        "genre": "drama",
    }
    test_app.post("/api/v1/books", json=book)
    book = {
        "title": "Forty Shades of Grey 7",
        "author": "E.L. James",
        "publication_year": 1599,
        "genre": "drama",
    }
    test_app.post("/api/v1/books", json=book)

    # Act
    response = test_app.get("/api/v1/books/search?title=forty")

    # Assert
    assert response.status_code == status.HTTP_200_OK

    response = json.loads(response.content)
    response = [Book(**item) for item in response.get("items")]
    assert len(response) == 1
    assert response[0].title == "Forty Shades of Grey 7"


def test_search_one_book_author_and_title(test_app: TestClient) -> None:
    """Test that search book endpoint returns 1 book when searched by title and author."""
    # Arrange
    book = {
        "title": "Fifty Shades of Grey 4",
        "author": "E.L. James",
        "publication_year": 1599,
        "genre": "drama",
    }
    test_app.post("/api/v1/books", json=book)
    book = {
        "title": "Forty Shades of Grey 7",
        "author": "E.L. James",
        "publication_year": 1599,
        "genre": "drama",
    }
    test_app.post("/api/v1/books", json=book)

    # Act
    response = test_app.get("/api/v1/books/search?author=james&title=fifty")

    # Assert
    assert response.status_code == status.HTTP_200_OK

    response = json.loads(response.content)
    response = [Book(**item) for item in response.get("items")]
    assert len(response) == 1
    assert response[0].title == "Fifty Shades of Grey 4"


def test_search_genre_filtered_out(test_app: TestClient) -> None:
    """Test that search book endpoint filers out genre '18+'."""
    # Arrange
    book = {
        "title": "Fifty Shades of Grey 4",
        "author": "E.L. James",
        "publication_year": 1599,
        "genre": "18+",
    }
    test_app.post("/api/v1/books", json=book)
    book = {
        "title": "Forty Shades of Grey 7",
        "author": "E.L. James",
        "publication_year": 1599,
        "genre": "18+",
    }
    test_app.post("/api/v1/books", json=book)

    # Act
    response = test_app.get("/api/v1/books/search?author=james&title=blue")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.text == '{"reason":"Books not found."}'


def test_search_no_author_and_title(test_app: TestClient) -> None:
    """Test that at least one of parameters author or title is required for the search endpoint."""
    # Act
    response = test_app.get("/api/v1/books/search")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.text == '{"reason":"At least one of parameters title or author is required."}'

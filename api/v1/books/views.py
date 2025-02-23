from typing import List

from fastapi import APIRouter, Body, Depends, status
from fastapi.responses import JSONResponse
from fastapi_pagination import Page, paginate
from sqlalchemy.orm import Session

from database.config import get_db
from database.crud.books import db_delete, db_get_by_id, db_get_by_ids, db_get_censored, db_insert, db_search, db_update
from models.book import Book
from schemas.book import BookCreate, BookGet, BooksWithGenres
from utils.logger import logger

router = APIRouter(prefix="/books")


@router.post("/", response_model=BookGet, status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreate = Body(...), db: Session = Depends(get_db)):
    """Endpoint to add a New Book. Books with the genre "Horror" cannot be added."""
    logger.info(f"Creating a book {book!s}")

    if book.genre.lower() == "horror":
        return JSONResponse(
            content={
                "reason": f"Books with genre {book.genre} cannot be added.",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    db_book = Book(**book.model_dump())
    db_insert(db, db_book)
    return db_book


@router.get("/", response_model=Page[BooksWithGenres], status_code=status.HTTP_200_OK)
async def get_all_books(db: Session = Depends(get_db)):
    """
    Endpoint to retrieve a List of All Books.

    Group books by genre and provide a count for each group.
    Mask titles for books with the genre "18+".
    """
    db_books_result = db_get_censored(db)
    logger.info(f"Found {len(db_books_result)} genres with books.")

    if not db_books_result:
        return JSONResponse(
            content={
                "reason": "No books in the library. Sorry!",
            },
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return paginate(db_books_result)


@router.put("/", response_model=List[BookGet], status_code=status.HTTP_200_OK)
async def update_books(books: List[BookGet] = Body(...), db: Session = Depends(get_db)):
    """
    Endpoint to update books by IDs. Supports multiple books at once.

    :param query: List of IDs separated by comma
    """
    logger.info(f"Updating books {books!s}")
    db_books = db_get_by_ids(db, [book.id for book in books])

    if len(db_books) < len(books):
        return JSONResponse(
            content={"reason": "Not all books found. Update is allowed only for existing books."},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    for book in books:
        db_update(db, book)

    db_books = db_get_by_ids(db, [book.id for book in books])

    return db_books


@router.delete("/{book_id}", status_code=status.HTTP_200_OK)
async def delete_book(book_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to delete book by IDs.

    :param book_id: book ID, integer.

    """
    logger.info(f"Deleting the book with ID {book_id!s}")

    db_book = db_get_by_id(db, book_id)

    if not db_book:
        return JSONResponse(
            content={"reason": f"Book with ID {book_id} not found."},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    count = db.query(Book).filter(Book.genre == db_book.genre).count()

    if count == 1:
        return JSONResponse(
            content={"reason": f"Cannnot delete the last book from the genre {db_book.genre}."},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    db_delete(db, db_book.id)  # type: ignore # noqa: RET503


@router.get("/search", response_model=Page[BookGet])
async def search_books(title: str = "", author: str = "", db: Session = Depends(get_db)):
    """
    Endpoint to search for Books by Title or Author.

    At least one of Title or Author is required.
    Cannot search for books with the genre "18+".
    Case insensitive, partial.

    :param title: title of the book
    :param author: author of the book
    """
    logger.info(f"Searching for books with parameters: title={title!s}, author={author!s}.")

    if not (title or author):
        return JSONResponse(
            content={"reason": "At least one of parameters title or author is required."},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    db_books = db_search(db=db, title=title, author=author)

    if not db_books:
        return JSONResponse(
            content={"reason": "Books not found."},
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return paginate(db_books)

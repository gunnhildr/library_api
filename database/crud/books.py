from typing import List

from sqlalchemy import and_, func, not_
from sqlalchemy.orm import Session

from models.book import BookModel
from schemas.book import BooksWithGenres, CensoredBook


def db_insert(db: Session, data: object) -> None:
    """
    Insert a book.

    : param data: data to insert.
    """
    db.add(data)
    db.commit()


def db_update(db: Session, data) -> int:
    """
    Update a book.

    : param data: data to update.
    """
    result = db.query(BookModel).filter(BookModel.id == data.id).update(data.model_dump())
    db.commit()

    return result


def db_get_censored(db: Session) -> List[BooksWithGenres]:
    """
    Return all books grouped by genre and provide a count for each group.

    Mask titles for books with the genre "18+".
    """
    result: BooksWithGenres = []

    genres = (db.query(BookModel.genre, func.count().label("count")).group_by(BookModel.genre).order_by(BookModel.genre)).all()

    for genre in genres:
        books = db.query(BookModel).filter(BookModel.genre == genre[0]).all()

        aggregated_books = BooksWithGenres(
            genre=genre[0],
            count=genre[1],
            books=[CensoredBook.model_validate(book.__dict__) for book in books],
        )

        result.append(aggregated_books)
    return result


def db_get_by_ids(db: Session, ids: List[int]) -> List[BookModel]:
    """
    Get books by ID.

    :param ids: list if IDs.
    """
    return db.query(BookModel).filter(BookModel.id.in_(ids)).all()


def db_get_by_id(db: Session, _id: int) -> BookModel:
    """
    Get book by ID.

    :param _id: book ID.
    """
    return db.query(BookModel).filter(BookModel.id == _id).first()


def db_search(db: Session, title: str = None, author: str = None) -> List[BookModel]:
    """
    Endpoint to search for Books by Title or Author.

    At least one of Title or Author is required.
    Cannot search for books with the genre "18+".
    Case insensitive, partial.

    :param title: title of the book.
    :param author: author of the book.
    """
    filters = and_(
        func.lower(BookModel.title).contains(title.lower()) if title else True,
        func.lower(BookModel.author).contains(author.lower()) if author else True,
        not_((BookModel.genre).contains("18+")),
    )

    return db.query(BookModel).filter(filters).all()


def db_delete(db: Session, _id: int) -> None:
    """
    Delete the book by ID.

    :param _id: book ID.
    """
    db.query(BookModel).filter(BookModel.id == _id).delete()
    db.commit()

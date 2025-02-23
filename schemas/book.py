from typing import List

from pydantic import BaseModel, root_validator


class BookCreate(BaseModel):
    """Create book pydantic model."""

    title: str
    author: str
    publication_year: int
    genre: str


class Book(BookCreate):
    """Book pydantic model."""

    id: int


class CensoredBook(BookCreate):
    """Censored book pydantic model: title is 'CENSORED' if genre is '18+'."""

    id: int

    @root_validator(pre=True)
    def hide_title_if_18(cls, values):
        if values.get("genre") == "18+":
            values["title"] = "CENSORED"
        return values


class BooksWithGenres(BaseModel):
    """Pydantic model for list of Censored Books grouped by genre and showing count."""

    books: List[CensoredBook]
    genre: str
    count: int

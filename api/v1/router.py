from fastapi import APIRouter

from api.v1.books.views import router as books_router

api_router = APIRouter()

api_router.include_router(books_router, prefix="/books")

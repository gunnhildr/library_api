# Library Management API.

API for managing a library of books. The API provides functionality to manage a collection of books, each with a title, author, publication year, and genre.

## Main features:

- **Add a New Book.** Books with the genre "Horror" cannot be added.
- **Retrieve a List of All Books.** List is grouped by genre and provides a count for each group. Masks titles for books with the genre "18+".
- **Update a Book by Its ID.** Supports updating multiple books at once.
- **Delete a Book by Its ID.** Cannot delete the last remaining book in a genre.
- **Search for Books by Title or Author.** Cannot search for books with the genre "18+".
 
## How to run

1. Install and configure docker and vscode: https://code.visualstudio.com/docs/containers/overview
2. Open in devcontainers. See https://code.visualstudio.com/docs/devcontainers/containers for more info.
3. In terminal: `uvicorn main:app --port 8081 --reload`.
4. (Optional) Run db_script.py to get some data in the DB.



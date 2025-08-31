# Library System API

A simple FastAPI-based library system for managing books and users.

## Requirements
- Python 3.8+
- FastAPI
- Uvicorn

## Installation
1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd library-system
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the API
Start the server with Uvicorn:
```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## API Endpoints
- `GET /books` — List all books
- `POST /books` — Add a new book
- `PUT /books/{id}` — Update a book
- `DELETE /books/{id}` — Delete a book
- `POST /users/register` — Register a new user

## Project Structure
```
library-system/
  main.py
  models.py
  database.py
  schemas.py
  routes/
    books.py
    users.py
  requirements.txt
  README.md
```

## Notes
- This is a learning project. Feel free to expand features and add more routes.

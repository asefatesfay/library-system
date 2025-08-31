from fastapi import APIRouter

router = APIRouter()
books_db = [
    {"id": 1, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "price": 12.99},
    {"id": 2, "title": "To Kill a Mockingbird", "author": "Harper Lee", "price": 14.99}
]

@router.get("/books")
def get_all_books():
    return {"books": books_db}

@router.get("/books/{id}")
def get_book(id: int):
    book = next((b for b in books_db if b["id"] == id), None)
    if book:
        return {"book": book}
    return {"error": "Book not found"}

@router.post("/books")
def create_book(book: dict):
    book["id"] = len(books_db) + 1
    books_db.append(book)
    return {"book": book}

@router.put("/books/{id}")
def update_book(id: int, updated_book: dict):
    book = next((b for b in books_db if b["id"] == id), None)
    if book:
        book.update(updated_book)
        return {"book": book}
    return {"error": "Book not found"}

@router.delete("/books/{id}")
def delete_book(id: int):
    index = next((i for i, b in enumerate(books_db) if b["id"] == id), None)
    if index is not None:
        books_db.pop(index)
        return {"message": "Book deleted"}
    return {"error": "Book not found"}

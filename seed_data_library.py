from sqlalchemy.orm import Session
from database import SessionLocal, User, Book, BookCopy, UserRoleEnum, BookCopyStatusEnum
from auth import hash_password
from datetime import datetime
import uuid

def create_seed_data():
    """Create initial seed data for the library system"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(User).first() or db.query(Book).first():
            print("Seed data already exists, skipping...")
            return
        
        # Create sample users (library members and staff)
        users_data = [
            {
                "email": "admin@library.com",
                "full_name": "Library Administrator",
                "role": UserRoleEnum.ADMIN,
                "password": "admin123",
                "phone": "+1-555-0001",
                "address": "123 Library Admin St, Book City, BC 12345"
            },
            {
                "email": "librarian@library.com",
                "full_name": "Jane Librarian",
                "role": UserRoleEnum.LIBRARIAN,
                "password": "librarian123",
                "phone": "+1-555-0002",
                "address": "456 Librarian Ave, Book City, BC 12345"
            },
            {
                "email": "member@library.com",
                "full_name": "John Member",
                "role": UserRoleEnum.MEMBER,
                "password": "member123",
                "phone": "+1-555-0003",
                "address": "789 Member Dr, Book City, BC 12345"
            },
            {
                "email": "alice.reader@email.com",
                "full_name": "Alice Reader",
                "role": UserRoleEnum.MEMBER,
                "password": "alice123",
                "phone": "+1-555-0004",
                "address": "321 Reading St, Book City, BC 12345"
            },
            {
                "email": "bob.bookworm@email.com", 
                "full_name": "Bob Bookworm",
                "role": UserRoleEnum.MEMBER,
                "password": "bob123",
                "phone": "+1-555-0005",
                "address": "654 Literature Ln, Book City, BC 12345"
            }
        ]
        
        for user_data in users_data:
            db_user = User(
                email=user_data["email"],
                full_name=user_data["full_name"],
                role=user_data["role"],
                hashed_password=hash_password(user_data["password"]),
                phone=user_data["phone"],
                address=user_data["address"]
            )
            db.add(db_user)
        
        # Create sample books with library-appropriate metadata
        books_data = [
            {
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "isbn": "978-0-7432-7356-5",
                "publisher": "Scribner",
                "publication_year": 1925,
                "genre": "Fiction",
                "description": "A classic American novel set in the Jazz Age.",
                "total_copies": 3
            },
            {
                "title": "To Kill a Mockingbird",
                "author": "Harper Lee",
                "isbn": "978-0-06-112008-4",
                "publisher": "J.B. Lippincott & Co.",
                "publication_year": 1960,
                "genre": "Fiction",
                "description": "A novel about racial injustice in the American South.",
                "total_copies": 2
            },
            {
                "title": "1984",
                "author": "George Orwell",
                "isbn": "978-0-452-28423-4",
                "publisher": "Secker & Warburg",
                "publication_year": 1949,
                "genre": "Dystopian Fiction",
                "description": "A dystopian social science fiction novel.",
                "total_copies": 4
            },
            {
                "title": "Pride and Prejudice",
                "author": "Jane Austen",
                "isbn": "978-0-14-143951-8",
                "publisher": "T. Egerton",
                "publication_year": 1813,
                "genre": "Romance",
                "description": "A romantic novel of manners.",
                "total_copies": 2
            },
            {
                "title": "The Catcher in the Rye",
                "author": "J.D. Salinger",
                "isbn": "978-0-316-76948-0",
                "publisher": "Little, Brown and Company",
                "publication_year": 1951,
                "genre": "Fiction",
                "description": "A controversial coming-of-age story.",
                "total_copies": 2
            },
            {
                "title": "Lord of the Flies",
                "author": "William Golding",
                "isbn": "978-0-571-05686-2",
                "publisher": "Faber & Faber",
                "publication_year": 1954,
                "genre": "Allegorical Fiction",
                "description": "A story about British boys stranded on an island.",
                "total_copies": 3
            },
            {
                "title": "Jane Eyre",
                "author": "Charlotte Brontë",
                "isbn": "978-0-14-144114-6",
                "publisher": "Smith, Elder & Co.",
                "publication_year": 1847,
                "genre": "Gothic Fiction",
                "description": "A bildungsroman following the experiences of its title character.",
                "total_copies": 2
            },
            {
                "title": "The Hobbit",
                "author": "J.R.R. Tolkien",
                "isbn": "978-0-547-92822-7",
                "publisher": "George Allen & Unwin",
                "publication_year": 1937,
                "genre": "Fantasy",
                "description": "A children's fantasy novel about Bilbo Baggins.",
                "total_copies": 4
            },
            {
                "title": "Fahrenheit 451",
                "author": "Ray Bradbury",
                "isbn": "978-1-451-67331-9",
                "publisher": "Ballantine Books",
                "publication_year": 1953,
                "genre": "Dystopian Fiction",
                "description": "A dystopian novel about a future where books are banned.",
                "total_copies": 2
            },
            {
                "title": "Brave New World",
                "author": "Aldous Huxley",
                "isbn": "978-0-06-085052-4",
                "publisher": "Chatto & Windus",
                "publication_year": 1932,
                "genre": "Science Fiction",
                "description": "A dystopian novel set in a futuristic World State.",
                "total_copies": 3
            }
        ]
        
        # Create books and their copies
        for book_data in books_data:
            total_copies = book_data.pop("total_copies")
            
            # Create the book record
            db_book = Book(
                **book_data,
                total_copies=total_copies,
                available_copies=total_copies
            )
            db.add(db_book)
            db.flush()  # Get the book ID
            
            # Create individual copies of each book
            for copy_num in range(1, total_copies + 1):
                barcode = f"{db_book.isbn.replace('-', '')}{copy_num:03d}" if db_book.isbn else f"BOOK{db_book.id:04d}{copy_num:03d}"
                
                book_copy = BookCopy(
                    book_id=db_book.id,
                    barcode=barcode,
                    status=BookCopyStatusEnum.AVAILABLE,
                    condition_notes="Good condition"
                )
                db.add(book_copy)
        
        db.commit()
        
        # Count total copies created
        total_book_copies = db.query(BookCopy).count()
        
        print("✅ Library seed data created successfully!")
        print(f"📚 Created {len(books_data)} book titles with {total_book_copies} physical copies")
        print("👥 Created 5 users:")
        print("   - admin@library.com (Admin)")
        print("   - librarian@library.com (Librarian)")
        print("   - member@library.com (Member)")
        print("   - alice.reader@email.com (Member)")
        print("   - bob.bookworm@email.com (Member)")
        print("🏛️ Library is ready for operation!")
        
    except Exception as e:
        print(f"❌ Error creating seed data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_seed_data()

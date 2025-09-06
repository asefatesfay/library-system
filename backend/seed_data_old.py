from sqlalchemy.orm import Session
from database import SessionLocal, User, Book, UserRoleEnum
from auth import hash_password

def create_seed_data():
    """Create initial seed data for the database"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(User).first() or db.query(Book).first():
            print("Seed data already exists, skipping...")
            return
        
        # Create sample users
        users_data = [
            {
                "email": "admin@library.com",
                "full_name": "Library Administrator",
                "role": UserRoleEnum.ADMIN,
                "password": "admin123"
            },
            {
                "email": "librarian@library.com",
                "full_name": "Jane Librarian",
                "role": UserRoleEnum.LIBRARIAN,
                "password": "librarian123"
            },
            {
                "email": "member@library.com",
                "full_name": "John Member",
                "role": UserRoleEnum.MEMBER,
                "password": "member123"
            }
        ]
        
        for user_data in users_data:
            db_user = User(
                email=user_data["email"],
                full_name=user_data["full_name"],
                role=user_data["role"],
                hashed_password=hash_password(user_data["password"])
            )
            db.add(db_user)
        
        # Create sample books
        books_data = [
            {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "price": 12.99},
            {"title": "To Kill a Mockingbird", "author": "Harper Lee", "price": 14.99},
            {"title": "1984", "author": "George Orwell", "price": 13.50},
            {"title": "Pride and Prejudice", "author": "Jane Austen", "price": 11.99},
            {"title": "The Catcher in the Rye", "author": "J.D. Salinger", "price": 15.99},
            {"title": "Lord of the Flies", "author": "William Golding", "price": 12.50},
            {"title": "Jane Eyre", "author": "Charlotte Brontë", "price": 13.99},
            {"title": "The Hobbit", "author": "J.R.R. Tolkien", "price": 16.99},
            {"title": "Fahrenheit 451", "author": "Ray Bradbury", "price": 14.50},
            {"title": "Brave New World", "author": "Aldous Huxley", "price": 13.75},
            {"title": "The Lord of the Rings", "author": "J.R.R. Tolkien", "price": 25.99},
            {"title": "Harry Potter and the Philosopher's Stone", "author": "J.K. Rowling", "price": 17.99},
            {"title": "The Chronicles of Narnia", "author": "C.S. Lewis", "price": 19.99},
            {"title": "Dune", "author": "Frank Herbert", "price": 18.50},
            {"title": "The Hitchhiker's Guide to the Galaxy", "author": "Douglas Adams", "price": 14.99}
        ]
        
        for book_data in books_data:
            db_book = Book(**book_data)
            db.add(db_book)
        
        db.commit()
        print("✅ Seed data created successfully!")
        print("📚 Created 15 books")
        print("👥 Created 3 users:")
        print("   - admin@library.com (password: admin123)")
        print("   - librarian@library.com (password: librarian123)")
        print("   - member@library.com (password: member123)")
        
    except Exception as e:
        print(f"❌ Error creating seed data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_seed_data()

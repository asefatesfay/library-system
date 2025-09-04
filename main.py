from fastapi import FastAPI
from routes.books import router as books_router
from routes.users import router as users_router
from routes.auth import router as auth_router
from database import create_tables
from seed_data import create_seed_data

app = FastAPI(title="Library Management System", version="1.0.0")

# Create database tables and seed data on startup
@app.on_event("startup")
def startup_event():
    print("🚀 Starting up...")
    create_tables()
    print("📊 Tables created...")
    create_seed_data()
    print("✅ Startup complete!")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(books_router, tags=["Books"])
app.include_router(users_router, tags=["Users"])
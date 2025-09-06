from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from routes.books import router as books_router
from routes.users import router as users_router
from routes.auth import router as auth_router
from routes.loans import router as loans_router
from routes.holds import router as holds_router
from routes.members import router as members_router
from routes.fines import router as fines_router
from routes.notifications import router as notifications_router
from database import create_tables
from seed_data import create_seed_data

app = FastAPI(title="Library Management System", version="1.0.0")

# Create database tables and seed data on startup
@app.on_event("startup")
def startup_event():
    print("🚀 Starting up...")
    import os
    database_url = os.getenv('DATABASE_URL')
    print(f"Database URL configured: {bool(database_url)}")
    print(f"Full DATABASE_URL: {database_url}")
    print(f"JWT_SECRET_KEY configured: {bool(os.getenv('JWT_SECRET_KEY'))}")
    
    try:
        create_tables()
        print("📊 Tables created...")
        create_seed_data()
        print("✅ Startup complete!")
    except Exception as e:
        print(f"❌ Startup error: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()

@app.get("/")
async def root():
    """Redirect to API documentation"""
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(books_router, tags=["Books"])
app.include_router(loans_router, tags=["Loans"])
app.include_router(holds_router, tags=["Holds"])
app.include_router(fines_router, tags=["Fines"])
app.include_router(notifications_router, tags=["Notifications"])
app.include_router(members_router, tags=["Members"])
app.include_router(users_router, tags=["Users"])
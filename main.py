from fastapi import FastAPI
from routes.books import router as books_router
from routes.users import router as users_router

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

app.include_router(books_router)
app.include_router(users_router)
from pydantic import BaseModel
from typing import Optional

class BookBase(BaseModel):
    title: str
    author: str
    price: float
    description: Optional[str] = None

class BookCreate(BookBase):
    pass

class BookUpdate(BookBase):
    title: Optional[str] = None
    author: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None

class Book(BookBase):
    id: int
    class Config:
        from_attributes = True

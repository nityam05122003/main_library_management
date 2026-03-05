from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class BookBase(BaseModel):
    title: str


class BookCreate(BookBase):
    pass


class BookResponse(BookCreate):
    id: int

    class Config:
        orm_mode = True


class IssuedBookCreate(BaseModel):
    student_id: int
    book_id: int
    due_date: date


class IssuedBookResponse(BaseModel):
    id: int
    student_id: int
    book_id: int
    issue_date: datetime
    due_date: Optional[date]
    return_date: Optional[datetime]
    is_returned: bool
    fine_amount: int

    class Config:
        orm_mode = True

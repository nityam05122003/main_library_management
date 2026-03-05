from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.college_engine import get_db
from app.models.college import Book, User
from app.schemas.book import BookCreate, BookResponse

router = APIRouter(prefix="/book", tags=["book"])


def authenticate_user(db: Session, username: str, password: str, college_id: int):
    user = db.query(User).filter(User.username == username, User.college_id == college_id).first()
    if not user or user.password != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user


def get_admin_or_librarian_user(db: Session = Depends(get_db), username: str = Header(...), password: str = Header(...), x_college_id: int = Header(...)):
    user = authenticate_user(db, username, password, x_college_id)
    if user.role not in ['admin', 'librarian']:
        raise HTTPException(status_code=403, detail="Admin or Librarian required")
    return user


@router.post("/")
def create_book(book: BookCreate, db: Session = Depends(get_db), x_college_id: int = Header(...), current_user: User = Depends(get_admin_or_librarian_user)):
    db_book = Book(**book.dict(), college_id=x_college_id, created_by=current_user.id)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


@router.get("/", response_model=List[BookResponse])
def get_all_books(db: Session = Depends(get_db), x_college_id: int = Header(...)):
    return db.query(Book).filter(Book.college_id == x_college_id).all()


@router.get("/{book_id}", response_model=BookResponse)
def get_book_by_id(book_id: int, db: Session = Depends(get_db), x_college_id: int = Header(...)):
    book_obj = db.query(Book).filter(Book.id == book_id, Book.college_id == x_college_id).first()
    if not book_obj:
        raise HTTPException(status_code=404, detail="book not found")
    return book_obj


@router.put("/{book_id}", response_model=BookResponse)
def update_book(book: BookCreate, book_id: int, db: Session = Depends(get_db), x_college_id: int = Header(...)):
    book_obj = db.query(Book).filter(Book.id == book_id, Book.college_id == x_college_id).first()
    if not book_obj:
        raise HTTPException(status_code=404, detail="book not found")
    for key, value in book.dict().items():
        setattr(book_obj, key, value)
    db.commit()
    db.refresh(book_obj)
    return book_obj


@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db), x_college_id: int = Header(...), username: str = Header(...), password: str = Header(...)):
    user = authenticate_user(db, username, password, x_college_id)
    if user.role != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can delete book")
    book_obj = db.query(Book).filter(Book.id == book_id, Book.college_id == x_college_id).first()
    if not book_obj:
        raise HTTPException(status_code=404, detail="book not found")
    db.delete(book_obj)
    db.commit()
    return {"message": "Book deleted successfully"}

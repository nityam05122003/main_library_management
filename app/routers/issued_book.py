from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date
from app.db.college_engine import get_db
from app.models.college import IssuedBook, Student, Book, User
from app.schemas.book import IssuedBookCreate, IssuedBookResponse

router = APIRouter(prefix="/issued_book", tags=["issued_book"])


def get_admin_or_librarian_user(db: Session = Depends(get_db), username: str = Header(...), password: str = Header(...), x_college_id: int = Header(...)):
    user = db.query(User).filter(User.username == username, User.password == password, User.college_id == x_college_id).first()
    if not user or user.role not in ['admin', 'librarian']:
        raise HTTPException(status_code=403, detail="Only librarian or admin can perform this action")
    return user


@router.post("/", response_model=IssuedBookResponse)
def issue_book(data: IssuedBookCreate, db: Session = Depends(get_db), x_college_id: int = Header(...), current_user: User = Depends(get_admin_or_librarian_user)):
    student = db.query(Student).filter(Student.id == data.student_id, Student.college_id == x_college_id).first()
    book = db.query(Book).filter(Book.id == data.book_id, Book.college_id == x_college_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    existing = db.query(IssuedBook).filter(IssuedBook.student_id == data.student_id, IssuedBook.book_id == data.book_id, IssuedBook.is_returned == False).first()
    if existing:
        raise HTTPException(status_code=400, detail="Book already issued")
    issued = IssuedBook(student_id=data.student_id, book_id=data.book_id, due_date=data.due_date, college_id=x_college_id)
    db.add(issued)
    db.commit()
    db.refresh(issued)
    return issued


@router.put("/{issue_id}/return", response_model=IssuedBookResponse)
def return_book(issue_id: int, db: Session = Depends(get_db), x_college_id: int = Header(...)):
    issued = db.query(IssuedBook).filter(IssuedBook.id == issue_id, IssuedBook.college_id == x_college_id).first()
    if not issued:
        raise HTTPException(status_code=404, detail="Issued book not found")
    issued.is_returned = True
    issued.return_date = datetime.utcnow()
    if issued.due_date and issued.return_date.date() > issued.due_date:
        days_late = (issued.return_date.date() - issued.due_date).days
        issued.fine_amount = days_late * 5
    db.commit()
    db.refresh(issued)
    return issued


@router.get("/delayed", response_model=List[IssuedBookResponse])
def get_delayed_books(db: Session = Depends(get_db), x_college_id: int = Header(...)):
    return db.query(IssuedBook).filter(IssuedBook.is_returned == False, IssuedBook.due_date < date.today(), IssuedBook.college_id == x_college_id).all()


@router.get("/", response_model=List[IssuedBookResponse])
def get_all_issued_books(db: Session = Depends(get_db), x_college_id: int = Header(...)):
    return db.query(IssuedBook).filter(IssuedBook.college_id == x_college_id).all()

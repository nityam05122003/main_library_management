from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.db.college_engine import get_db
from app.models.college import Student, Book, IssuedBook, Department

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/")
def dashboard(db: Session = Depends(get_db), x_college_id: int = Header(...)):
    return {
        "total_students": db.query(Student).filter(Student.college_id == x_college_id).count(),
        "total_books": db.query(Book).filter(Book.college_id == x_college_id).count(),
        "issued_books": db.query(IssuedBook).filter(IssuedBook.is_returned == False, IssuedBook.college_id == x_college_id).count(),
    }


@router.get("/department-wise")
def department_dashboard(db: Session = Depends(get_db), x_college_id: int = Header(...)):
    result = db.query(Department.name, func.count(Student.id)).outerjoin(Student, and_(Student.department_id == Department.id, Student.college_id == x_college_id)).filter(Department.college_id == x_college_id).group_by(Department.name).all()
    return [{"department_name": row[0], "total_students": row[1]} for row in result]

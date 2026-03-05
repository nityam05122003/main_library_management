from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.college_engine import get_db
from app.models.college import IssuedBook, Student, User

router = APIRouter(prefix="/analytics", tags=["analytics"])


def get_current_user(db: Session = Depends(get_db), username: str = Header(...), password: str = Header(...), x_college_id: int = Header(...)):
    user = db.query(User).filter(User.username == username, User.password == password, User.college_id == x_college_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return user


@router.get("/student/{student_id}")
def student_analytics(student_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), x_college_id: int = Header(...)):
    if current_user.role == 'student' and current_user.id != student_id:
        raise HTTPException(status_code=403, detail="Access denied")
    student = db.query(Student).filter(Student.id == student_id, Student.college_id == x_college_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    total_issued = db.query(IssuedBook).filter(IssuedBook.student_id == student_id, IssuedBook.college_id == x_college_id).count()
    returned_late = db.query(IssuedBook).filter(IssuedBook.student_id == student_id, IssuedBook.is_returned == True, IssuedBook.fine_amount > 0, IssuedBook.college_id == x_college_id).count()
    returned_on_time = db.query(IssuedBook).filter(IssuedBook.student_id == student_id, IssuedBook.is_returned == True, IssuedBook.fine_amount == 0, IssuedBook.college_id == x_college_id).count()
    currently_issued = db.query(IssuedBook).filter(IssuedBook.student_id == student_id, IssuedBook.is_returned == False, IssuedBook.college_id == x_college_id).count()
    total_fine = db.query(func.coalesce(func.sum(IssuedBook.fine_amount), 0)).filter(IssuedBook.student_id == student_id, IssuedBook.college_id == x_college_id).scalar()
    return {"student_id": student_id, "total_issued": total_issued, "returned_on_time": returned_on_time, "returned_late": returned_late, "currently_issued": currently_issued, "total_fine_paid": total_fine}


@router.get("/top-students")
def top_students(db: Session = Depends(get_db), x_college_id: int = Header(...), username: str = Header(...), password: str = Header(...)):
    user = db.query(User).filter(User.username == username, User.password == password, User.college_id == x_college_id).first()
    if not user or user.role != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can view top students")
    result = db.query(IssuedBook.student_id, func.count(IssuedBook.id).label("total_books")).filter(IssuedBook.college_id == x_college_id).group_by(IssuedBook.student_id).order_by(func.count(IssuedBook.id).desc()).limit(5).all()
    return [{"student_id": row.student_id, "total_books": row.total_books} for row in result]


@router.get("/top-books")
def top_books(db: Session = Depends(get_db), x_college_id: int = Header(...)):
    result = db.query(IssuedBook.book_id, func.count(IssuedBook.id).label("issue_count")).filter(IssuedBook.college_id == x_college_id).group_by(IssuedBook.book_id).order_by(func.count(IssuedBook.id).desc()).limit(5).all()
    return [{"book_id": row.book_id, "issue_count": row.issue_count} for row in result]


@router.get("/monthly-fine")
def monthly_fine(db: Session = Depends(get_db), x_college_id: int = Header(...)):
    result = db.query(func.date_trunc('month', IssuedBook.return_date).label("month"), func.sum(IssuedBook.fine_amount).label("total_fine")).filter(IssuedBook.return_date != None, IssuedBook.college_id == x_college_id).group_by(func.date_trunc('month', IssuedBook.return_date)).all()
    return [{"month": row.month.strftime("%Y-%m") if row.month else None, "total_fine": float(row.total_fine or 0)} for row in result]


@router.get("/top-defaulters")
def top_defaulters(db: Session = Depends(get_db), x_college_id: int = Header(...)):
    result = db.query(IssuedBook.student_id, func.sum(IssuedBook.fine_amount).label("total_fine")).filter(IssuedBook.college_id == x_college_id).group_by(IssuedBook.student_id).order_by(func.sum(IssuedBook.fine_amount).desc()).limit(5).all()
    return [{"student_id": row.student_id, "total_fine": float(row.total_fine or 0)} for row in result]

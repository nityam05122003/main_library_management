from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.db.college_engine import get_db
from app.models.college import Student

router = APIRouter(prefix="/promotion", tags=["promotion"])


@router.post("/year")
def promote_year_students(db: Session = Depends(get_db), x_college_id: int = Header(...)):
    students = db.query(Student).filter(Student.college_id == x_college_id, Student.year != None).all()
    for student in students:
        if student.year < 3:
            student.year += 1
        else:
            student.year = None
    db.commit()
    return {"message": "Year promotion completed"}


@router.post("/semester")
def promote_semester_students(db: Session = Depends(get_db), x_college_id: int = Header(...)):
    students = db.query(Student).filter(Student.college_id == x_college_id, Student.semester != None).all()
    for student in students:
        if student.semester < 6:
            student.semester += 1
        else:
            student.semester = None
    db.commit()
    return {"message": "Semester promotion completed"}

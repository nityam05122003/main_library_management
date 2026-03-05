from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.college_engine import get_db
from app.models.college import Student, Department, User
from app.schemas.student import StudentCreate, StudentResponse

router = APIRouter(prefix="/student", tags=["student"])


def authenticate_user(db: Session, username: str, password: str, college_id: int):
    user = db.query(User).filter(User.username == username, User.college_id == college_id).first()
    if not user or user.password != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user


def get_admin_user(db: Session = Depends(get_db), username: str = Header(...), password: str = Header(...), x_college_id: int = Header(...)):
    user = authenticate_user(db, username, password, x_college_id)
    if user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.post("/")
def create_student(student: StudentCreate, db: Session = Depends(get_db), x_college_id: int = Header(...), current_user: User = Depends(get_admin_user)):
    department = db.query(Department).filter(Department.name == student.department_name, Department.college_id == x_college_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    student_data = student.dict()
    student_data.pop("department_name")
    db_student = Student(**student_data, department_id=department.id, college_id=x_college_id)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return {"id": db_student.id, "name": db_student.name, "email": db_student.email, "phone": db_student.phone, "year": db_student.year, "semester": db_student.semester, "academic_session": db_student.academic_session, "department_name": department.name}


@router.get("/", response_model=List[StudentResponse])
def get_all_student(db: Session = Depends(get_db), x_college_id: int = Header(...), username: str = Header(...), password: str = Header(...)):
    user = authenticate_user(db, username, password, x_college_id)
    if user.role != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can view students")
    students = db.query(Student).filter(Student.college_id == x_college_id).all()
    result = []
    for student in students:
        department = db.query(Department).filter(Department.id == student.department_id).first()
        result.append({"id": student.id, "name": student.name, "email": student.email, "phone": student.phone, "year": student.year, "semester": student.semester, "academic_session": student.academic_session, "department_name": department.name if department else None})
    return result


@router.get("/{student_id}", response_model=StudentResponse)
def get_student_by_id(student_id: int, db: Session = Depends(get_db), x_college_id: int = Header(...), username: str = Header(...), password: str = Header(...)):
    user = authenticate_user(db, username, password, x_college_id)
    if user.role != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can view student")
    student_obj = db.query(Student).filter(Student.id == student_id, Student.college_id == x_college_id).first()
    if not student_obj:
        raise HTTPException(status_code=404, detail="Student not found")
    department = db.query(Department).filter(Department.id == student_obj.department_id).first()
    return {"id": student_obj.id, "name": student_obj.name, "email": student_obj.email, "phone": student_obj.phone, "year": student_obj.year, "semester": student_obj.semester, "academic_session": student_obj.academic_session, "department_name": department.name if department else None}


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(student: StudentCreate, student_id: int, db: Session = Depends(get_db), x_college_id: int = Header(...), username: str = Header(...), password: str = Header(...)):
    user = authenticate_user(db, username, password, x_college_id)
    if user.role != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can update student")
    student_obj = db.query(Student).filter(Student.id == student_id, Student.college_id == x_college_id).first()
    if not student_obj:
        raise HTTPException(status_code=404, detail="Student not found")
    department = db.query(Department).filter(Department.name == student.department_name, Department.college_id == x_college_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    student_data = student.dict()
    student_data.pop("department_name")
    for key, value in student_data.items():
        setattr(student_obj, key, value)
    student_obj.department_id = department.id
    db.commit()
    db.refresh(student_obj)
    return {"id": student_obj.id, "name": student_obj.name, "email": student_obj.email, "phone": student_obj.phone, "year": student_obj.year, "semester": student_obj.semester, "academic_session": student_obj.academic_session, "department_name": department.name}


@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db), x_college_id: int = Header(...), username: str = Header(...), password: str = Header(...)):
    user = authenticate_user(db, username, password, x_college_id)
    if user.role != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can delete student")
    student_obj = db.query(Student).filter(Student.id == student_id, Student.college_id == x_college_id).first()
    if not student_obj:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(student_obj)
    db.commit()
    return {"message": "Student deleted successfully"}

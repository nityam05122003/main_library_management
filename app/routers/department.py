from fastapi import APIRouter, Header, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.college_engine import get_db
from app.models.college import Department

router = APIRouter(prefix="/department", tags=["department"]) 


@router.post("/")
def create_department(name: str, db: Session = Depends(get_db), x_college_id: int = Header(...)):
    existing = db.query(Department).filter(Department.name == name, Department.college_id == x_college_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Department already exists")
    dept = Department(name=name, college_id=x_college_id)
    try:
        db.add(dept)
        db.commit()
        db.refresh(dept)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Department created"}


@router.get("/all")
def list_departments(db: Session = Depends(get_db), x_college_id: int = Header(...), username: str = Header(...), password: str = Header(...)):
    from app.core.config import STATIC_SUPER_ADMINS
    # try super admin
    for admin in STATIC_SUPER_ADMINS:
        if admin["username"] == username and admin["password"] == password:
            return db.query(Department).filter(Department.college_id == x_college_id).all()

    # else authenticate college user
    from app.models.college import User
    user = db.query(User).filter(User.username == username, User.password == password, User.college_id == x_college_id).first()
    if not user or user.role != 'admin':
        raise HTTPException(status_code=403, detail="Only Super Admin or Admin can view departments")

    return db.query(Department).filter(Department.college_id == x_college_id).all()

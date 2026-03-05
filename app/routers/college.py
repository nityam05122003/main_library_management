from fastapi import APIRouter, Header, HTTPException
from sqlalchemy.orm import Session
from app.schemas.college import CollegeCreate
from app.core.config import STATIC_SUPER_ADMINS
from app.db.master import MasterSessionLocal
from app.models.master import College
from app.utils.db_utils import create_college_database, init_college_db
from app.models.college import CollegeBase

router = APIRouter(prefix="/college", tags=["college"]) 


def authenticate_super_admin(username: str, password: str):
    for admin in STATIC_SUPER_ADMINS:
        if admin["username"] == username and admin["password"] == password:
            return {"username": username, "role": "super_admin"}
    raise HTTPException(status_code=401, detail="Invalid super admin credentials")


@router.post("/")
def create_college(college: CollegeCreate, username: str = Header(...), password: str = Header(...)):
    authenticate_super_admin(username, password)
    db = MasterSessionLocal()
    db_name = f"college_{college.name.lower().replace(' ', '_')}"
    existing = db.query(College).filter(College.name == college.name).first()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="College already exists")

    new_college = College(name=college.name, db_name=db_name)
    db.add(new_college)
    db.commit()
    db.refresh(new_college)

    create_college_database(db_name)
    init_college_db(db_name, CollegeBase)

    db.close()

    return {"message": "College created successfully", "college_id": new_college.id}


@router.get("/")
def get_all_colleges(username: str = Header(...), password: str = Header(...)):
    authenticate_super_admin(username, password)
    db = MasterSessionLocal()
    colleges = db.query(College).all()
    db.close()
    return [
        {"id": c.id, "name": c.name, "db_name": c.db_name, "status": c.status, "created_at": c.created_at}
        for c in colleges
    ]


@router.delete("/{college_id}")
def delete_college(college_id: int, username: str = Header(...), password: str = Header(...)):
    authenticate_super_admin(username, password)
    db = MasterSessionLocal()
    college = db.query(College).filter(College.id == college_id).first()
    if not college:
        db.close()
        raise HTTPException(status_code=404, detail="College not found")
    db_name = college.db_name
    db.delete(college)
    db.commit()
    db.close()
    from app.utils.db_utils import drop_college_database
    drop_college_database(db_name)
    return {"message": "College deleted successfully"}

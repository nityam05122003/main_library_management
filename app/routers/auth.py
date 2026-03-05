from fastapi import APIRouter, Header, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate
from app.db.college_engine import get_db
from app.db.master import MasterSessionLocal
from app.models.college import User
from app.models.master import College
from app.core.config import STATIC_SUPER_ADMINS

router = APIRouter(prefix="/auth", tags=["auth"])


def authenticate_super_admin(username: str, password: str):
    for admin in STATIC_SUPER_ADMINS:
        if admin["username"] == username and admin["password"] == password:
            return {"username": username, "role": "super_admin"}
    raise HTTPException(status_code=401, detail="Invalid super admin credentials")


def authenticate_user(db: Session, username: str, password: str, college_id: int):
    user = db.query(User).filter(User.username == username, User.college_id == college_id).first()
    if not user or user.password != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user


@router.post("/login")
def login(username: str = Header(...), password: str = Header(...), x_college_id: int = Header(...), db: Session = Depends(get_db)):
    user = authenticate_user(db, username, password, x_college_id)
    return {"message": "Login successful", "role": user.role, "user_id": user.id}


@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db), x_college_id: int = Header(...)):
    master_db = MasterSessionLocal()
    college = master_db.query(College).filter(College.id == x_college_id).first()
    master_db.close()
    if not college:
        raise HTTPException(status_code=404, detail="College not found")

    existing_user = db.query(User).filter(User.username == user.username, User.college_id == x_college_id).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists in this college")

    new_user = User(username=user.username, password=user.password, role="student", college_id=x_college_id)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully", "user": {"id": new_user.id, "username": new_user.username, "role": new_user.role, "college_id": new_user.college_id}}


@router.post("/create-admin")
def create_admin(username: str, password: str, college_id: int, super_admin_username: str = Header(...), super_admin_password: str = Header(...)):
    authenticate_super_admin(super_admin_username, super_admin_password)
    engine = None
    from app.db.college_engine import get_engine_by_college_id
    engine = get_engine_by_college_id(college_id)
    SessionLocal = sessionmaker = None
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    old_admin = db.query(User).filter(User.role == 'admin', User.college_id == college_id).first()
    if old_admin:
        db.delete(old_admin)
        db.commit()
    admin = User(username=username, password=password, role='admin', college_id=college_id)
    db.add(admin)
    db.commit()
    db.close()
    return {"message": "College admin created/replaced successfully"}

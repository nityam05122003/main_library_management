from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import Depends, Header, HTTPException
from app.db.master import MasterSessionLocal
from app.models.master import College
from app.core.config import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT


def get_engine_by_college_id(college_id: int):
    db = MasterSessionLocal()
    college = db.query(College).filter(College.id == college_id).first()
    db.close()
    if not college:
        raise HTTPException(status_code=404, detail="College not found")
    db_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{college.db_name}"
    engine = create_engine(db_url)
    return engine


def get_db(x_college_id: int = Header(...)):
    engine = get_engine_by_college_id(x_college_id)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

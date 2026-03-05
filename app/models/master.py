from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db.master import MasterBase


class College(MasterBase):
    __tablename__ = "college"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    db_name = Column(String, unique=True)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

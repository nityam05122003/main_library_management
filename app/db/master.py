from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import MASTER_DB_URL

master_engine = create_engine(MASTER_DB_URL)
MasterSessionLocal = sessionmaker(bind=master_engine, autoflush=False, autocommit=False)
MasterBase = declarative_base()

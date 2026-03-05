import psycopg2
from datetime import datetime
from sqlalchemy import create_engine
from app.core.config import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT
from app.db.master import MasterBase, master_engine


def create_college_database(db_name: str):
    conn = psycopg2.connect(
        dbname="postgres",
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT
    )
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(f'CREATE DATABASE "{db_name}"')
    cursor.close()
    conn.close()


def drop_college_database(db_name: str):
    conn = psycopg2.connect(
        dbname="postgres",
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT
    )
    conn.autocommit = True
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT pg_terminate_backend(pid)
        FROM pg_stat_activity
        WHERE datname = '{db_name}'
        AND pid <> pg_backend_pid();
    """)

    cursor.execute(f'DROP DATABASE IF EXISTS "{db_name}"')
    cursor.close()
    conn.close()


def init_college_db(db_name: str, CollegeBase):
    db_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{db_name}"
    engine = create_engine(db_url)
    CollegeBase.metadata.create_all(bind=engine)

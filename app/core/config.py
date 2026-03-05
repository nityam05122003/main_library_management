from datetime import datetime

POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "123456"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
MASTER_DB = "master_db"

MASTER_DB_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{MASTER_DB}"

STATIC_SUPER_ADMINS = [
    {"username": "nitya", "password": "1234"},
    {"username": "nityanand", "password": "5678"}
]

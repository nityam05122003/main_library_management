from fastapi import FastAPI
from app.db.master import MasterBase, master_engine
from app.models.master import College

app = FastAPI(title="Student Management API - Modular")

# create master tables if not exist
MasterBase.metadata.create_all(bind=master_engine)

from app.routers import (
    college as college_router,
    auth as auth_router,
    department as department_router,
    student as student_router,
    book as book_router,
    issued_book as issued_book_router,
    dashboard as dashboard_router,
    analytics as analytics_router,
    exam as exam_router,
    promotion as promotion_router,
)

app.include_router(college_router.router)
app.include_router(auth_router.router)
app.include_router(department_router.router)
app.include_router(student_router.router)
app.include_router(book_router.router)
app.include_router(issued_book_router.router)
app.include_router(dashboard_router.router)
app.include_router(analytics_router.router)
app.include_router(exam_router.router)
app.include_router(promotion_router.router)


@app.get("/")
def root():
    return {"message": "Student Management API - Modular Multi DB"}

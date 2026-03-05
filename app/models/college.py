from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Float, UniqueConstraint, Date
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

CollegeBase = declarative_base()


class Student(CollegeBase):
    __tablename__ = "student"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(Integer, nullable=False)
    college_id = Column(Integer, nullable=False)
    year = Column(Integer, nullable=True)
    semester = Column(Integer, nullable=True)
    academic_session = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("department.id"))

    department_rel = relationship("Department", back_populates="students")
    issued_books = relationship("IssuedBook", back_populates="student", cascade="all, delete-orphan")
    exam_scores = relationship("ExamScore", back_populates="student", cascade="all, delete-orphan")


class Department(CollegeBase):
    __tablename__ = "department"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    college_id = Column(Integer, nullable=False)
    __table_args__ = (
        UniqueConstraint("name", "college_id", name="unique_department_per_college"),)

    students = relationship("Student", back_populates="department_rel")


class Book(CollegeBase):
    __tablename__ = "book"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    college_id = Column(Integer, nullable=False)
    created_by = Column(Integer, nullable=True)

    issued_books = relationship("IssuedBook", back_populates="book", cascade="all, delete-orphan")


class IssuedBook(CollegeBase):
    __tablename__ = "issued_book"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student.id"))
    book_id = Column(Integer, ForeignKey("book.id"))
    issue_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(Date, nullable=True)
    return_date = Column(DateTime, nullable=True)
    is_returned = Column(Boolean, default=False)
    fine_amount = Column(Integer, default=0)
    college_id = Column(Integer, nullable=False)

    student = relationship("Student", back_populates="issued_books", lazy="joined")
    book = relationship("Book", back_populates="issued_books", lazy="joined")


class User(CollegeBase):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    password = Column(String)
    role = Column(String)
    college_id = Column(Integer, nullable=False)


ROLE_STUDENT = "student"
ROLE_LIBRARIAN = "librarian"
ROLE_ADMIN = "admin"
ROLE_SUPER_ADMIN = "super_admin"


class ExamScore(CollegeBase):
    __tablename__ = "exam_score"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student.id"))
    college_id = Column(Integer, nullable=False)
    exam_type = Column(String)
    hindi = Column(Integer, default=0)
    english = Column(Integer, default=0)
    maths = Column(Integer, default=0)
    science = Column(Integer, default=0)
    social_science = Column(Integer, default=0)
    total = Column(Integer, default=0)
    average = Column(Integer, default=0)
    percentage = Column(Integer, default=0)
    student = relationship("Student", back_populates="exam_scores")
    grade_point = Column(Float, default=0)
    is_pass = Column(Boolean, default=True)

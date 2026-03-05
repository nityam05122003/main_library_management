from pydantic import BaseModel
from typing import Optional


class ExamScoreCreate(BaseModel):
    student_id: int
    exam_type: str
    hindi: int
    english: int
    maths: int
    science: int
    social_science: int
    year: Optional[int] = None
    semester: Optional[int] = None


class ExamScoreResponse(BaseModel):
    id: int
    student_id: int
    exam_type: str
    hindi: int
    english: int
    maths: int
    science: int
    social_science: int
    total: int
    average: float
    percentage: float
    grade_point: float
    is_pass: bool

    class Config:
        orm_mode = True

from pydantic import BaseModel, EmailStr, field_validator, model_validator
from typing import Optional
from datetime import date


class StudentBase(BaseModel):
    name: str
    email: EmailStr
    phone: int
    year: Optional[int] = None
    semester: Optional[int] = None
    academic_session: str
    department_name: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, value):
        if not value.endswith("@gmail.com"):
            raise ValueError("email must end with @gmail.com")
        return value

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, value):
        if len(str(value)) != 10:
            raise ValueError("phone number must be 10 digits")
        return value

    @model_validator(mode="after")
    def validate_year_semester(self):
        if self.year is None and self.semester is None:
            raise ValueError("Either year or semester must be provided")

        if self.year is not None and self.semester is not None:
            raise ValueError("Provide either year OR semester, not both")
        return self

    @field_validator("academic_session")
    @classmethod
    def validate_session(cls, v):
        if len(v) != 7 or "-" not in v:
            raise ValueError("Academic session must be in format YYYY-YY (example: 2025-26)")
        return v


class StudentCreate(StudentBase):
    pass


class StudentResponse(StudentCreate):
    id: int
    name: str
    email: EmailStr
    phone: int
    year: Optional[int]
    semester: Optional[int]
    academic_session: str
    department_name: str

    class Config:
        orm_mode = True

from pydantic import BaseModel


class CollegeCreate(BaseModel):
    name: str

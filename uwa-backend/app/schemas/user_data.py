from pydantic import BaseModel, Field


class SaveUserCourseInput(BaseModel):
    course: str = Field(min_length=1, max_length=16)
    section: str = Field(min_length=1, max_length=32)

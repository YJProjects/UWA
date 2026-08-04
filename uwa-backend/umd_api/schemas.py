"""Response models for Testudo course search results."""

from pydantic import BaseModel, ConfigDict, Field


class CourseSection(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    class_number: str = Field(alias="classNumber")
    section: str
    schedule: str
    campus: str
    location: str
    delivery_mode: str = Field(alias="deliveryMode")
    instructor: str
    available_seats: int | None = Field(alias="availableSeats")
    total_seats: int | None = Field(alias="totalSeats")


class CourseResult(BaseModel):
    id: str
    code: str
    title: str
    school: str
    term: str
    sections: list[CourseSection]

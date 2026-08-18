"""Course section and seat-availability model."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Section:
    course_code: str
    number: str
    instructor: str | None = None
    meeting_time: str | None = None
    location: str | None = None
    open_seats: int | None = None
    waitlist_count: int | None = None
    total_seats: int | None = None

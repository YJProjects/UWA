"""Course section and meeting models."""

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Meeting:
    days: tuple[str, ...]
    start_time: str
    end_time: str
    location: str | None = None


@dataclass(frozen=True, slots=True)
class Section:
    course_code: str
    section_code: str
    instructors: tuple[str, ...] = field(default_factory=tuple)
    meetings: tuple[Meeting, ...] = field(default_factory=tuple)
    open_seats: int | None = None
    total_seats: int | None = None
    waitlist_count: int | None = None

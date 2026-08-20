"""Course catalog model."""

from dataclasses import dataclass, field

from .section import Section


@dataclass(frozen=True, slots=True)
class Course:
    code: str
    semester: str
    title: str
    description: str | None = None
    credits: int | None = None
    sections: tuple[Section, ...] = field(default_factory=tuple)

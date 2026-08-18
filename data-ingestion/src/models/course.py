"""Course catalog model."""

from dataclasses import dataclass, field

from .section import Section


@dataclass(frozen=True, slots=True)
class Course:
    code: str
    name: str
    semester: str
    description: str | None = None
    credits: str | None = None
    sections: tuple[Section, ...] = field(default_factory=tuple)

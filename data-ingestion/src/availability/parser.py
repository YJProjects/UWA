"""Extract section availability from a Testudo course page."""

from src.catalog.parser import parse_catalog
from src.models import Section


def parse_availability(html: str, semester: str) -> list[Section]:
    courses = parse_catalog(html, semester)
    return [section for course in courses for section in course.sections]

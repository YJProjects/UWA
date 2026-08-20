"""Extract section availability from a Testudo course page."""
from src.models import Section


def parse_availability(html: str, semester: str) -> list[Section]:
    #TODO
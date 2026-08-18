"""Parse Testudo catalog HTML into domain models."""

import re

from bs4 import BeautifulSoup, Tag

from src.models import Course, Section


def _text(node: Tag, selector: str) -> str | None:
    match = node.select_one(selector)
    value = match.get_text(" ", strip=True) if match else ""
    return value or None


def _integer(node: Tag, selector: str) -> int | None:
    value = _text(node, selector)
    match = re.search(r"\d+", value.replace(",", "")) if value else None
    return int(match.group()) if match else None


def _section(node: Tag, course_code: str) -> Section:
    number = _text(node, ".section-id") or ""
    instructor = _text(node, ".section-instructor")
    days = _text(node, ".section-days")
    start = _text(node, ".class-start-time")
    end = _text(node, ".class-end-time")
    building = _text(node, ".building-code")
    room = _text(node, ".class-room")
    return Section(
        course_code=course_code,
        number=number,
        instructor=instructor,
        meeting_time=" ".join(filter(None, (days, start, end))) or None,
        location=" ".join(filter(None, (building, room))) or None,
        open_seats=_integer(node, ".open-seats-count"),
        waitlist_count=_integer(node, ".waitlist-count"),
        total_seats=_integer(node, ".total-seats-count"),
    )


def parse_catalog(html: str, semester: str) -> list[Course]:
    soup = BeautifulSoup(html, "html.parser")
    courses: list[Course] = []
    for node in soup.select(".course[id]"):
        code = str(node.get("id", "")).upper()
        if not code:
            continue
        courses.append(
            Course(
                code=code,
                name=_text(node, ".course-title") or code,
                semester=semester,
                description=_text(node, ".approved-course-text"),
                credits=_text(node, ".course-min-credits"),
                sections=tuple(
                    _section(section, code) for section in node.select(".section")
                ),
            )
        )
    return courses

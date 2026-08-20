"""Parse Testudo catalog HTML into domain models."""

from collections.abc import Iterable

from bs4 import BeautifulSoup, PageElement, Tag

from src.models import Course, Meeting, Section


def _get_text(element: PageElement | None, default: str | None = None) -> str | None:
    if element is None:
        return default

    value = element.get_text(strip=True)
    return value or default


def _get_int(element: PageElement | None) -> int | None:
    value = _get_text(element)
    if value is None:
        return None

    try:
        return int(value.replace(",", ""))
    except ValueError:
        return None


def _parse_days(days_text: str | None) -> tuple[str, ...]:
    return tuple(days_text) if days_text else tuple()


def _parse_meeting(meeting_data: Tag) -> Meeting:
    return Meeting(
        days=_parse_days(_get_text(meeting_data.select_one(".section-days"))),
        start_time=_get_text(meeting_data.select_one(".class-start-time"), "") or "",
        end_time=_get_text(meeting_data.select_one(".class-end-time"), "") or "",
        location=_get_text(
            meeting_data.select_one(".section-class-building-group")
        ),
    )


def _parse_section(section_data: Tag, course_code: str) -> Section:
    meeting_rows = section_data.select(".class-days-container .row")

    return Section(
        course_code=course_code,
        section_code=_get_text(section_data.select_one(".section-id"), "") or "",
        instructors=tuple(
            instructor.get_text(strip=True)
            for instructor in section_data.select(".section-instructor")
            if instructor.get_text(strip=True)
        ),
        meetings=tuple(_parse_meeting(row) for row in meeting_rows),
        open_seats=_get_int(section_data.select_one(".open-seats-count")),
        total_seats=_get_int(section_data.select_one(".total-seats-count")),
        waitlist_count=_get_int(section_data.select_one(".waitlist-count")),
    )


def _parse_course(unparsed_course: Tag, semester: str) -> Course:
    course_code = _get_text(unparsed_course.select_one(".course-id"))
    if course_code is None:
        course_code = str(unparsed_course.get("id", "")).strip()

    return Course(
        code=course_code,
        semester=semester,
        title=_get_text(unparsed_course.select_one(".course-title"), "") or "",
        description=_get_text(
            unparsed_course.select_one(".approved-course-text")
        ),
        credits=_get_int(unparsed_course.select_one(".course-min-credits")),
        sections=tuple(
            _parse_section(section_data, course_code)
            for section_data in unparsed_course.select(".section")
        ),
    )


def parse_all_course_prefixes(page: str) -> list[str]:
    soup = BeautifulSoup(page, "html.parser")
    return [
        element.get_text(strip=True)
        for element in soup.select("span.prefix-abbrev")
        if element.get_text(strip=True)
    ]


def parse_courses(
    unparsed_courses: Iterable[Tag], semester: str
) -> list[Course]:
    """Convert course elements from a Testudo response into domain models."""
    return [
        _parse_course(unparsed_course, semester)
        for unparsed_course in unparsed_courses
    ]


def parse_catalog(page: str, semester: str) -> list[Course]:
    """Parse all courses contained in a Testudo HTML response."""
    soup = BeautifulSoup(page, "html.parser")
    return parse_courses(soup.select("div.course"), semester)

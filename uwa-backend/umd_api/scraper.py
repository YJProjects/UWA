"""Scrape public course and seat data from Testudo."""

from __future__ import annotations

import re
import time
from functools import lru_cache

import requests
from bs4 import BeautifulSoup, Tag

from .schemas import CourseResult, CourseSection

BASE_URL = "https://app.testudo.umd.edu/soc"
DEFAULT_SEMESTER = "202608"
REQUEST_TIMEOUT = (10, 60)
CACHE_SECONDS = 60
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; UWA course search prototype)",
    "Accept": "text/html,application/xhtml+xml",
}


class TestudoScraperError(RuntimeError):
    """Testudo could not be fetched or its response could not be parsed."""


def normalize_course_prefix(value: str) -> str:
    prefix = re.sub(r"\s+", "", value).upper()
    if not re.fullmatch(r"[A-Z]{4}(?:[0-9]{1,3}[A-Z]?)?", prefix):
        raise ValueError(
            "Enter four department letters followed by up to three digits "
            "and an optional suffix, for example CMSC13 or CMSC131."
        )
    return prefix


def validate_semester(value: str) -> str:
    semester = value.strip()
    if not re.fullmatch(r"\d{6}", semester):
        raise ValueError(
            "semester must use Testudo YYYYMM format, for example 202608."
        )
    return semester


def _fetch_soup(session: requests.Session, url: str) -> BeautifulSoup:
    try:
        response = session.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise TestudoScraperError(f"Unable to fetch Testudo URL: {url}") from exc
    return BeautifulSoup(response.text, "html.parser")


def _node_text(node: Tag | BeautifulSoup, selector: str, default: str = "") -> str:
    match = node.select_one(selector)
    return match.get_text(" ", strip=True) if match else default


def _node_int(node: Tag, selector: str) -> int | None:
    value = _node_text(node, selector)
    match = re.search(r"\d+", value.replace(",", ""))
    return int(match.group()) if match else None


def _format_term(semester: str) -> str:
    year, term_code = semester[:4], semester[4:]
    term_names = {
        "01": "Spring",
        "05": "Summer",
        "08": "Fall",
        "12": "Winter",
    }
    return f"{term_names.get(term_code, term_code)} {year}"


def _discover_course_ids(
    session: requests.Session,
    prefix: str,
    semester: str,
) -> list[str]:
    department = prefix[:4]
    soup = _fetch_soup(
        session,
        f"{BASE_URL}/{semester}/{department}/{prefix}",
    )
    return [
        str(course["id"]).upper()
        for course in soup.select(".course[id]")
        if str(course["id"]).upper().startswith(prefix)
    ]


def _delivery_mode(section: Tag) -> str:
    classes = set(section.get("class", []))
    if "delivery-online" in classes:
        return "Online"
    if "delivery-blended" in classes:
        return "Blended"
    if "delivery-f2f" in classes:
        return "In person"
    return "TBA"


def _campus(section: Tag) -> str:
    notes = " ".join(
        note.get_text(" ", strip=True) for note in section.select(".section-text")
    ).lower()
    if "shady grove" in notes:
        return "Shady Grove"
    if "southern maryland" in notes:
        return "Southern Maryland"
    return "College Park"


def _parse_section(section: Tag, course_code: str) -> CourseSection:
    number = _node_text(section, ".section-id")
    schedules: list[str] = []
    locations: list[str] = []

    for meeting in section.select(".class-days-container > .row"):
        days = _node_text(meeting, ".section-days")
        start = _node_text(meeting, ".class-start-time")
        end = _node_text(meeting, ".class-end-time")
        if days or start or end:
            time_range = f"{start}–{end}" if start and end else start or end
            schedules.append(" ".join(part for part in (days, time_range) if part))

        building = _node_text(meeting, ".building-code")
        room = _node_text(meeting, ".class-room")
        location = " ".join(part for part in (building, room) if part)
        if location and location not in locations:
            locations.append(location)

    instructors = [
        instructor.get_text(" ", strip=True)
        for instructor in section.select(".section-instructor")
        if instructor.get_text(" ", strip=True)
    ]
    delivery_mode = _delivery_mode(section)

    return CourseSection(
        id=f"{course_code.lower()}-section-{number.lower()}",
        class_number=number,
        section=f"Section {number}",
        schedule="; ".join(schedules) or "TBA",
        campus=_campus(section),
        location="; ".join(locations)
        or ("Online" if delivery_mode == "Online" else "TBA"),
        delivery_mode=delivery_mode,
        instructor=", ".join(instructors) or "TBA",
        available_seats=_node_int(section, ".open-seats-count"),
        total_seats=_node_int(section, ".total-seats-count"),
    )


def _parse_course(soup: BeautifulSoup, semester: str) -> CourseResult:
    course = soup.select_one(".course[id]")
    if course is None:
        raise TestudoScraperError("Testudo returned a page without a course record.")

    code = str(course["id"]).upper()
    term = _format_term(semester)
    term_slug = term.lower().replace(" ", "-")

    return CourseResult(
        id=f"{code.lower()}-{term_slug}",
        code=code,
        title=_node_text(course, ".course-title"),
        school=_node_text(soup, ".course-prefix-name"),
        term=term,
        sections=[
            _parse_section(section, code) for section in course.select(".section")
        ],
    )


@lru_cache(maxsize=128)
def _search_cached(
    prefix: str,
    semester: str,
    cache_bucket: int,
) -> tuple[CourseResult, ...]:
    del cache_bucket
    with requests.Session() as session:
        session.headers.update(HEADERS)
        course_ids = _discover_course_ids(session, prefix, semester)
        return tuple(
            _parse_course(
                _fetch_soup(
                    session,
                    f"{BASE_URL}/{semester}/{course_id[:4]}/{course_id}",
                ),
                semester,
            )
            for course_id in course_ids
        )


def search_courses(
    partial_course_string: str,
    semester: str = DEFAULT_SEMESTER,
) -> list[CourseResult]:
    prefix = normalize_course_prefix(partial_course_string)
    validated_semester = validate_semester(semester)
    cache_bucket = int(time.time() // CACHE_SECONDS)
    return list(_search_cached(prefix, validated_semester, cache_bucket))

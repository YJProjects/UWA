"""Persistence operations for ingestion jobs."""

from collections.abc import Iterable
from datetime import datetime, time
from typing import Any

from psycopg import Cursor
from psycopg.types.json import Jsonb

from src.database.connection import Database
from src.models import Course, Section


class IngestionRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    @staticmethod
    def _parse_time(value: str) -> time | None:
        if not value:
            return None

        normalized = value.strip().upper()
        for time_format in ("%I:%M%p", "%H:%M"):
            try:
                return datetime.strptime(normalized, time_format).time()
            except ValueError:
                continue
        return None

    @staticmethod
    def _fetch_all(cursor: Cursor[Any]) -> list[dict[str, Any]]:
        return list(cursor.fetchall())

    def _upsert_terms(
        self, cursor: Cursor[Any], courses: list[Course]
    ) -> dict[str, Any]:
        term_codes = sorted({course.semester for course in courses})
        cursor.execute(
            """
            INSERT INTO course_data.terms (term_code)
            SELECT input.term_code
            FROM jsonb_to_recordset(%s) AS input(term_code text)
            ON CONFLICT (term_code) DO UPDATE
            SET term_code = EXCLUDED.term_code
            RETURNING id, term_code
            """,
            (Jsonb([{"term_code": code} for code in term_codes]),),
        )
        return {
            row["term_code"]: row["id"] for row in self._fetch_all(cursor)
        }

    def _upsert_courses(
        self, cursor: Cursor[Any], courses: list[Course]
    ) -> dict[str, Any]:
        unique_courses = {course.code: course for course in courses}
        payload = [
            {
                "course_code": course.code,
                "title": course.title,
                "description": course.description,
                "credits": course.credits,
            }
            for course in unique_courses.values()
        ]
        cursor.execute(
            """
            INSERT INTO course_data.courses (
                course_code,
                title,
                description,
                credits
            )
            SELECT
                input.course_code,
                input.title,
                input.description,
                input.credits
            FROM jsonb_to_recordset(%s) AS input(
                course_code text,
                title text,
                description text,
                credits integer
            )
            ON CONFLICT (course_code) DO UPDATE
            SET title = EXCLUDED.title,
                description = EXCLUDED.description,
                credits = EXCLUDED.credits,
                updated_at = NOW()
            RETURNING id, course_code
            """,
            (Jsonb(payload),),
        )
        return {
            row["course_code"]: row["id"]
            for row in self._fetch_all(cursor)
        }

    def _upsert_offerings(
        self,
        cursor: Cursor[Any],
        courses: list[Course],
        course_ids: dict[str, Any],
        term_ids: dict[str, Any],
    ) -> dict[tuple[str, str], Any]:
        payload = [
            {
                "course_id": str(course_ids[course.code]),
                "term_id": str(term_ids[course.semester]),
            }
            for course in courses
        ]
        cursor.execute(
            """
            INSERT INTO course_data.course_offerings (course_id, term_id)
            SELECT input.course_id, input.term_id
            FROM jsonb_to_recordset(%s) AS input(
                course_id uuid,
                term_id uuid
            )
            ON CONFLICT (course_id, term_id) DO UPDATE
            SET updated_at = NOW()
            RETURNING id, course_id, term_id
            """,
            (Jsonb(payload),),
        )
        return {
            (str(row["course_id"]), str(row["term_id"])): row["id"]
            for row in self._fetch_all(cursor)
        }

    def _upsert_sections(
        self,
        cursor: Cursor[Any],
        courses: list[Course],
        course_ids: dict[str, Any],
        term_ids: dict[str, Any],
        offering_ids: dict[tuple[str, str], Any],
    ) -> tuple[
        dict[tuple[str, str], Any],
        list[tuple[Any, Section]],
    ]:
        sections: list[tuple[Any, Section]] = []
        for course in courses:
            offering_key = (
                str(course_ids[course.code]),
                str(term_ids[course.semester]),
            )
            offering_id = offering_ids[offering_key]
            sections.extend(
                (offering_id, section) for section in course.sections
            )

        if not sections:
            return {}, sections

        payload = [
            {
                "course_offering_id": str(offering_id),
                "section_code": section.section_code,
                "open_seats": section.open_seats,
                "total_seats": section.total_seats,
                "waitlist_count": section.waitlist_count,
            }
            for offering_id, section in sections
        ]
        cursor.execute(
            """
            INSERT INTO course_data.sections AS existing (
                course_offering_id,
                section_code,
                open_seats,
                total_seats,
                waitlist_count,
                last_checked_at,
                last_changed_at
            )
            SELECT
                input.course_offering_id,
                input.section_code,
                input.open_seats,
                input.total_seats,
                input.waitlist_count,
                NOW(),
                NOW()
            FROM jsonb_to_recordset(%s) AS input(
                course_offering_id uuid,
                section_code text,
                open_seats integer,
                total_seats integer,
                waitlist_count integer
            )
            ON CONFLICT (course_offering_id, section_code) DO UPDATE
            SET open_seats = EXCLUDED.open_seats,
                total_seats = EXCLUDED.total_seats,
                waitlist_count = EXCLUDED.waitlist_count,
                last_checked_at = NOW(),
                last_changed_at = CASE
                    WHEN existing.open_seats IS DISTINCT FROM EXCLUDED.open_seats
                      OR existing.total_seats IS DISTINCT FROM EXCLUDED.total_seats
                      OR existing.waitlist_count IS DISTINCT FROM EXCLUDED.waitlist_count
                    THEN NOW()
                    ELSE existing.last_changed_at
                END,
                updated_at = NOW()
            RETURNING id, course_offering_id, section_code
            """,
            (Jsonb(payload),),
        )
        section_ids = {
            (str(row["course_offering_id"]), row["section_code"]): row["id"]
            for row in self._fetch_all(cursor)
        }
        return section_ids, sections

    def _replace_instructors(
        self,
        cursor: Cursor[Any],
        sections: list[tuple[Any, Section]],
        section_ids: dict[tuple[str, str], Any],
    ) -> None:
        all_section_ids = list(section_ids.values())
        cursor.execute(
            """
            DELETE FROM course_data.section_instructors
            WHERE section_id IN (
                SELECT value::uuid FROM jsonb_array_elements_text(%s)
            )
            """,
            (Jsonb([str(section_id) for section_id in all_section_ids]),),
        )

        instructor_names = sorted(
            {
                name
                for _, section in sections
                for name in section.instructors
            }
        )
        if not instructor_names:
            return

        cursor.execute(
            """
            INSERT INTO course_data.instructors (name)
            SELECT input.name
            FROM jsonb_to_recordset(%s) AS input(name text)
            ON CONFLICT (name) DO UPDATE
            SET name = EXCLUDED.name
            RETURNING id, name
            """,
            (Jsonb([{"name": name} for name in instructor_names]),),
        )
        instructor_ids = {
            row["name"]: row["id"] for row in self._fetch_all(cursor)
        }

        link_payload = []
        for offering_id, section in sections:
            section_id = section_ids[
                (str(offering_id), section.section_code)
            ]
            link_payload.extend(
                {
                    "section_id": str(section_id),
                    "instructor_id": str(instructor_ids[name]),
                }
                for name in dict.fromkeys(section.instructors)
            )

        cursor.execute(
            """
            INSERT INTO course_data.section_instructors (
                section_id,
                instructor_id
            )
            SELECT input.section_id, input.instructor_id
            FROM jsonb_to_recordset(%s) AS input(
                section_id uuid,
                instructor_id uuid
            )
            ON CONFLICT DO NOTHING
            """,
            (Jsonb(link_payload),),
        )

    def _replace_meetings(
        self,
        cursor: Cursor[Any],
        sections: list[tuple[Any, Section]],
        section_ids: dict[tuple[str, str], Any],
    ) -> None:
        cursor.execute(
            """
            DELETE FROM course_data.section_meetings
            WHERE section_id IN (
                SELECT value::uuid FROM jsonb_array_elements_text(%s)
            )
            """,
            (Jsonb([str(section_id) for section_id in section_ids.values()]),),
        )

        meeting_payload = []
        for offering_id, section in sections:
            section_id = section_ids[
                (str(offering_id), section.section_code)
            ]
            for meeting in section.meetings:
                start_time = self._parse_time(meeting.start_time)
                end_time = self._parse_time(meeting.end_time)
                meeting_payload.append(
                    {
                        "section_id": str(section_id),
                        "days": "".join(meeting.days) or None,
                        "start_time": (
                            start_time.isoformat() if start_time else None
                        ),
                        "end_time": end_time.isoformat() if end_time else None,
                        "location": meeting.location,
                    }
                )

        if not meeting_payload:
            return

        cursor.execute(
            """
            INSERT INTO course_data.section_meetings (
                section_id,
                days,
                start_time,
                end_time,
                location
            )
            SELECT
                input.section_id,
                input.days,
                input.start_time,
                input.end_time,
                input.location
            FROM jsonb_to_recordset(%s) AS input(
                section_id uuid,
                days text,
                start_time time,
                end_time time,
                location text
            )
            """,
            (Jsonb(meeting_payload),),
        )

    def save_courses(self, courses: Iterable[Course]) -> int:
        """Bulk-upsert courses and nested catalog data in one transaction."""
        course_list = list(
            {
                (course.semester, course.code): course
                for course in courses
            }.values()
        )
        if not course_list:
            return 0

        with self.database.connection() as connection:
            with connection.cursor() as cursor:
                term_ids = self._upsert_terms(cursor, course_list)
                course_ids = self._upsert_courses(cursor, course_list)
                offering_ids = self._upsert_offerings(
                    cursor, course_list, course_ids, term_ids
                )
                section_ids, sections = self._upsert_sections(
                    cursor,
                    course_list,
                    course_ids,
                    term_ids,
                    offering_ids,
                )
                if sections:
                    self._replace_instructors(
                        cursor, sections, section_ids
                    )
                    self._replace_meetings(cursor, sections, section_ids)

        return len(course_list)

    def save_availability(self, sections: Iterable[Section]) -> int:
        raise NotImplementedError(
            "Availability history persistence is not implemented"
        )

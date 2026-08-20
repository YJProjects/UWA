"""Persistence operations for ingestion jobs."""

from collections.abc import Iterable
from datetime import datetime, time
from typing import Any

from psycopg import Cursor

from src.database.connection import Database
from src.models import Course, Section


class IngestionRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    @staticmethod
    def _returned_id(cursor: Cursor[Any]) -> Any:
        row = cursor.fetchone()
        if row is None:
            raise RuntimeError("Database upsert did not return an id")
        return row["id"]

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

    def _upsert_term(self, cursor: Cursor[Any], term_code: str) -> Any:
        cursor.execute(
            """
            INSERT INTO course_data.terms (term_code)
            VALUES (%s)
            ON CONFLICT (term_code) DO UPDATE
            SET term_code = EXCLUDED.term_code
            RETURNING id
            """,
            (term_code,),
        )
        return self._returned_id(cursor)

    def _upsert_course(self, cursor: Cursor[Any], course: Course) -> Any:
        cursor.execute(
            """
            INSERT INTO course_data.courses (
                course_code,
                title,
                description,
                credits
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (course_code) DO UPDATE
            SET title = EXCLUDED.title,
                description = EXCLUDED.description,
                credits = EXCLUDED.credits,
                updated_at = NOW()
            RETURNING id
            """,
            (course.code, course.title, course.description, course.credits),
        )
        return self._returned_id(cursor)

    def _upsert_offering(
        self, cursor: Cursor[Any], course_id: Any, term_id: Any
    ) -> Any:
        cursor.execute(
            """
            INSERT INTO course_data.course_offerings (course_id, term_id)
            VALUES (%s, %s)
            ON CONFLICT (course_id, term_id) DO UPDATE
            SET updated_at = NOW()
            RETURNING id
            """,
            (course_id, term_id),
        )
        return self._returned_id(cursor)

    def _upsert_section(
        self, cursor: Cursor[Any], offering_id: Any, section: Section
    ) -> Any:
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
            VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
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
            RETURNING id
            """,
            (
                offering_id,
                section.section_code,
                section.open_seats,
                section.total_seats,
                section.waitlist_count,
            ),
        )
        return self._returned_id(cursor)

    def _replace_instructors(
        self, cursor: Cursor[Any], section_id: Any, section: Section
    ) -> None:
        cursor.execute(
            "DELETE FROM course_data.section_instructors WHERE section_id = %s",
            (section_id,),
        )

        for instructor_name in dict.fromkeys(section.instructors):
            cursor.execute(
                """
                INSERT INTO course_data.instructors (name)
                VALUES (%s)
                ON CONFLICT (name) DO UPDATE
                SET name = EXCLUDED.name
                RETURNING id
                """,
                (instructor_name,),
            )
            instructor_id = self._returned_id(cursor)
            cursor.execute(
                """
                INSERT INTO course_data.section_instructors (
                    section_id,
                    instructor_id
                )
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
                """,
                (section_id, instructor_id),
            )

    def _replace_meetings(
        self, cursor: Cursor[Any], section_id: Any, section: Section
    ) -> None:
        cursor.execute(
            "DELETE FROM course_data.section_meetings WHERE section_id = %s",
            (section_id,),
        )

        for meeting in section.meetings:
            cursor.execute(
                """
                INSERT INTO course_data.section_meetings (
                    section_id,
                    days,
                    start_time,
                    end_time,
                    location
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    section_id,
                    "".join(meeting.days) or None,
                    self._parse_time(meeting.start_time),
                    self._parse_time(meeting.end_time),
                    meeting.location,
                ),
            )

    def save_courses(self, courses: Iterable[Course]) -> int:
        """Upsert courses and all nested catalog data in one transaction."""
        saved_count = 0
        term_ids: dict[str, Any] = {}

        with self.database.connection() as connection:
            with connection.cursor() as cursor:
                for course in courses:
                    term_id = term_ids.get(course.semester)
                    if term_id is None:
                        term_id = self._upsert_term(cursor, course.semester)
                        term_ids[course.semester] = term_id

                    course_id = self._upsert_course(cursor, course)
                    offering_id = self._upsert_offering(
                        cursor, course_id, term_id
                    )

                    for section in course.sections:
                        section_id = self._upsert_section(
                            cursor, offering_id, section
                        )
                        self._replace_instructors(cursor, section_id, section)
                        self._replace_meetings(cursor, section_id, section)

                    saved_count += 1

        return saved_count

    def save_availability(self, sections: Iterable[Section]) -> int:
        raise NotImplementedError(
            "Availability history persistence is not implemented"
        )

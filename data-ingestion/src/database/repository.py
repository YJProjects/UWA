"""Repository boundary for ingestion persistence.

Concrete upsert statements belong here once the shared PostgreSQL schema and
migrations are finalized.
"""

from collections.abc import Iterable

from src.database.connection import Database
from src.models import Course, Section


class IngestionRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def save_courses(self, courses: Iterable[Course]) -> int:
        raise NotImplementedError("Course schema and upsert policy are not finalized")

    def save_availability(self, sections: Iterable[Section]) -> int:
        raise NotImplementedError(
            "Section schema and availability history policy are not finalized"
        )

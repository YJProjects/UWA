"""Build and persist the complete course catalog for a Testudo semester."""

import logging

from src.catalog.scraper import CatalogScraper
from src.database.connection import Database
from src.database.repository import IngestionRepository
from src.models import Course


logger = logging.getLogger(__name__)


def create_semester_data(
    semester: str, scraper: CatalogScraper | None = None
) -> list[Course]:
    """Fetch and parse every course published for ``semester``."""

    def fetch(active_scraper: CatalogScraper) -> list[Course]:
        courses: list[Course] = []
        course_prefixes = active_scraper.fetch_course_prefixes(semester)
        logger.info("Found %s course prefixes", len(course_prefixes))

        for prefix in course_prefixes:
            logger.info("Scraping course prefix %s", prefix.upper())
            courses.extend(
                active_scraper.fetch_courses_from_prefix(semester, prefix)
            )

        logger.info("Scraped %s courses for term %s", len(courses), semester)
        return courses

    if scraper is not None:
        return fetch(scraper)

    with CatalogScraper() as owned_scraper:
        return fetch(owned_scraper)


def ingest_semester_data(
    semester: str,
    scraper: CatalogScraper | None = None,
    repository: IngestionRepository | None = None,
) -> int:
    """Scrape a semester and persist its complete catalog graph."""
    logger.info("Catalog ingestion started for term %s", semester)
    courses = create_semester_data(semester, scraper=scraper)
    active_repository = repository or IngestionRepository(Database())
    saved_count = active_repository.save_courses(courses)
    logger.info(
        "Catalog ingestion completed for term %s: %s courses saved",
        semester,
        saved_count,
    )
    return saved_count

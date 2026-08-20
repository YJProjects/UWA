"""HTTP client for Testudo catalog pages."""

from typing import Any

import requests

from src.config import Settings, settings
from src.models import Course

import src.catalog.catalog_parser as catalog_parser


SEARCH_FILTERS: dict[str, str] = {
    "sectionId": "",
    "_openSectionsOnly": "on",
    "creditCompare": ">=",
    "credits": "0.0",
    "courseLevelFilter": "ALL",
    "instructor": "",
    "_facetoface": "on",
    "_blended": "on",
    "_online": "on",
    "courseStartCompare": "",
    "courseStartHour": "",
    "courseStartMin": "",
    "courseStartAM": "",
    "courseEndHour": "",
    "courseEndMin": "",
    "courseEndAM": "",
    "teachingCenter": "ALL",
    "_classDay1": "on",
    "_classDay2": "on",
    "_classDay3": "on",
    "_classDay4": "on",
    "_classDay5": "on",
}


class CatalogScraper:
    def __init__(self, config: Settings = settings) -> None:
        self.config = config
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    def _base_url(self) -> str:
        if not self.config.testudo_base_url:
            raise ValueError("TESTUDO_BASE_URL is required")
        return self.config.testudo_base_url.rstrip("/")

    def _get(self, url: str, **kwargs: Any) -> requests.Response:
        response = self.session.get(
            url,
            timeout=self.config.request_timeout_seconds,
            **kwargs,
        )
        response.raise_for_status()
        return response

    def fetch_course_prefixes(self, semester: str) -> list[str]:
        response = self._get(f"{self._base_url()}/{semester}")
        return catalog_parser.parse_all_course_prefixes(response.text)

    def fetch_courses_from_prefix(
        self, semester: str, prefix: str
    ) -> list[Course]:
        params = {
            **SEARCH_FILTERS,
            "courseId": prefix.upper(),
            "termId": semester,
        }
        response = self._get(
            f"{self._base_url()}/search",
            params=params,
        )
        return catalog_parser.parse_catalog(response.text, semester)

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "CatalogScraper":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

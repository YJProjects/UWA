"""HTTP client for individual Testudo course pages."""

import requests

from src.config import Settings, settings


class AvailabilityScraper:
    def __init__(self, config: Settings = settings) -> None:
        self.config = config
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "UWA data-ingestion/1.0"

    def fetch(self, semester: str, course_code: str) -> str:
        code = course_code.upper()
        url = f"{self.config.testudo_base_url}/{semester}/{code[:4]}/{code}"
        response = self.session.get(
            url, timeout=self.config.request_timeout_seconds
        )
        response.raise_for_status()
        return response.text

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "AvailabilityScraper":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

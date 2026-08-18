"""HTTP client for Testudo catalog pages."""

import requests

from src.config import Settings, settings


class CatalogScraper:
    def __init__(self, config: Settings = settings) -> None:
        self.config = config
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "UWA data-ingestion/1.0"

    def fetch(self, semester: str, department: str) -> str:
        url = f"{self.config.testudo_base_url}/{semester}/{department.upper()}"
        response = self.session.get(
            url, timeout=self.config.request_timeout_seconds
        )
        response.raise_for_status()
        return response.text

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "CatalogScraper":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

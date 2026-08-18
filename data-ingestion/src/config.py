"""Environment-backed service configuration."""

from dataclasses import dataclass
import logging
import os

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class Settings:
    database_url: str | None = os.getenv("DATABASE_URL")
    testudo_base_url: str | None = os.getenv("TESTUDO_BASE_URL")

    request_timeout_seconds: float = float(
        os.getenv("REQUEST_TIMEOUT_SECONDS", "30")
    )


settings = Settings()


def validate_config() -> None:
    logger.info(
        "Configuration loaded | testudo_url=%s | timeout=%ss | database_configured=%s",
        settings.testudo_base_url,
        settings.request_timeout_seconds,
        settings.database_url is not None,
    )

    if settings.database_url is None:
        logger.critical("Database URL not configured.")
        raise RuntimeError("DATABASE_URL environment variable is required.")

    if settings.testudo_base_url is None:
        logger.critical("Testudo base URL not configured.")
        raise RuntimeError("TESTUDO_BASE_URL environment variable is required.")
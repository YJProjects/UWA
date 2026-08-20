"""ASGI and command-line entry points for data ingestion."""

import argparse
import hmac
import logging
from collections.abc import Sequence

from fastapi import FastAPI, Header, HTTPException, status

from src.catalog.create_semester_data import ingest_semester_data
from src.config import settings, validate_config


app = FastAPI(title="UWA Data Ingestion")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    force=True,
)

validate_config()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/trigger_catalog_scraper")
def trigger_catalog_scraper(
    semester: str = "202608",
    authorization: str | None = Header(default=None),
) -> dict[str, int | str]:
    expected_authorization = f"Bearer {settings.cron_secret}"
    if authorization is None or not hmac.compare_digest(
        authorization, expected_authorization
    ):
        raise HTTPException(status_code=401, detail="Unauthorized")

    courses_saved = ingest_semester_data(semester)
    return {
        "status": status.HTTP_200_OK,
        "semester": semester,
        "courses_saved": courses_saved,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a data ingestion job")
    parser.add_argument("job", choices=("catalog", "availability"))
    parser.add_argument(
        "--semester",
        default="202608",
        help="Testudo term code used by the catalog job (default: 202608)",
    )
    args = parser.parse_args(argv)
    logging.getLogger(__name__).info("%s ingestion requested", args.job)

    if args.job == "catalog":
        ingest_semester_data(args.semester)
    else:
        logging.getLogger(__name__).warning(
            "Availability ingestion is not implemented"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""ASGI and command-line entry points for data ingestion."""

import argparse
import logging
from collections.abc import Sequence

from fastapi import FastAPI

from src.config import validate_config


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


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a data ingestion job")
    parser.add_argument("job", choices=("catalog", "availability"))
    args = parser.parse_args(argv)
    logging.getLogger(__name__).info("%s ingestion requested", args.job)
    logging.getLogger(__name__).warning(
        "Persistence is pending the shared database schema"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

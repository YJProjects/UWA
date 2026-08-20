"""Synchronous PostgreSQL connection management for ingestion jobs."""

from contextlib import contextmanager
from typing import Iterator

import psycopg
from psycopg import Connection
from psycopg.rows import dict_row

from src.config import Settings, settings


class Database:
    def __init__(self, config: Settings = settings) -> None:
        if not config.database_url:
            raise ValueError("DATABASE_URL is required")
        self.database_url = config.database_url

    @contextmanager
    def connection(self) -> Iterator[Connection]:
        with psycopg.connect(
            self.database_url, row_factory=dict_row
        ) as connection:
            yield connection

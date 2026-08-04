from typing import Any, Mapping, Sequence

from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from app.config import DATABASE_URL

QueryParameters = Mapping[str, Any] | Sequence[Any]


class Database:
    """Manage a PostgreSQL connection pool and execute parameterized queries."""

    def __init__(
        self,
        *,
        min_size: int = 1,
        max_size: int = 2,
    ) -> None:
        self.database_url = DATABASE_URL
        if not self.database_url:
            raise ValueError("DATABASE_URL is not configured in .env file")

        self.min_size = min_size
        self.max_size = max_size
        self._pool: AsyncConnectionPool | None = None

    async def close(self) -> None:
        """Close every connection in the pool."""
        if self._pool is None:
            return

        await self._pool.close()
        self._pool = None

    async def query(
        self,
        statement: str,
        parameters: QueryParameters | None = None,
        require_output: bool = False,
    ) -> list[dict[str, Any]] | None:
        """Run a SELECT-like statement and return all rows as dictionaries."""
        pool = self._require_pool()

        async with pool.connection() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    statement,
                    parameters if parameters is not None else (),
                )

                if not require_output:
                    return None
                rows = await cursor.fetchall()

        return [dict(row) for row in rows]

    async def execute(
        self,
        statement: str,
        parameters: QueryParameters | None = None,
    ) -> int:
        """Run a write/DDL statement and return the affected row count."""
        pool = self._require_pool()

        async with pool.connection() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    statement,
                    parameters if parameters is not None else (),
                )
                return cursor.rowcount
 
    def _require_pool(self) -> AsyncConnectionPool:
        if self._pool is None:
            raise RuntimeError("Database is not connected; call connect() first")
        return self._pool

    async def connect(self) -> None:
        """Open the connection pool."""
        if self._pool is not None:
            return

        self._pool = AsyncConnectionPool(
            conninfo=self.database_url,
            min_size=self.min_size,
            max_size=self.max_size,
            open=False,
            kwargs={"row_factory": dict_row},
        )

        try:
            await self._pool.open(wait=True)
        except Exception:
            self._pool = None
            raise

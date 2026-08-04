# Database Guide

The `Database` class in `app/db/database.py` provides asynchronous PostgreSQL
access using a connection pool. It supports parameterized read and write
operations and returns query results as dictionaries.

## Requirements

Install the project dependencies:

```bash
pip install -r requirements.txt
```

The database implementation uses Psycopg 3 and `psycopg_pool`.

## Configuration

Add the PostgreSQL connection URL to the project's `.env` file:

```dotenv
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

Do not commit a `.env` file containing real credentials.

`Database()` loads this variable when it is instantiated. It raises
`ValueError` if `DATABASE_URL` is missing.

## FastAPI setup

Create one `Database` instance for the application and manage it through the
FastAPI lifespan. This opens the pool when the application starts and closes it
cleanly during shutdown.

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.database import Database


database = Database(min_size=1, max_size=10)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    app.state.database = database

    try:
        yield
    finally:
        await database.close()


app = FastAPI(lifespan=lifespan)
```

`min_size` is the number of connections the pool keeps ready. `max_size` limits
the total number of connections it may open.

## Reading data

Use `query()` for statements that return rows:

```python
async def get_user_by_email(email: str):
    rows = await database.query(
        """
        SELECT id, email, created_at
        FROM users
        WHERE email = %(email)s
        """,
        {"email": email},
    )

    return rows[0] if rows else None
```

The result is a `list[dict[str, Any]]`. An empty result set returns an empty
list.

Positional parameters are also supported:

```python
rows = await database.query(
    "SELECT id, email FROM users WHERE id = %s",
    (user_id,),
)
```

Always pass user-provided values through the `parameters` argument. Do not build
SQL by concatenating or formatting those values into the statement.

## Writing data

Use `execute()` for inserts, updates, deletes, and schema statements:

```python
affected_rows = await database.execute(
    """
    UPDATE users
    SET email = %(email)s
    WHERE id = %(user_id)s
    """,
    {
        "email": new_email,
        "user_id": user_id,
    },
)
```

`execute()` returns the cursor's affected row count. PostgreSQL may return `-1`
when a row count cannot be determined for a statement.

To return inserted data, use `query()` with PostgreSQL's `RETURNING` clause:

```python
rows = await database.query(
    """
    INSERT INTO users (email, password_hash)
    VALUES (%(email)s, %(password_hash)s)
    RETURNING id, email, created_at
    """,
    {
        "email": email,
        "password_hash": password_hash,
    },
)

created_user = rows[0]
```

## API reference

### `Database(min_size=1, max_size=2)`

Creates the database manager. The constructor reads `DATABASE_URL`, but it does
not open any connections.

The small default maximum is intentional for serverless deployments, where
multiple function instances can each own a pool. Prefer a hosted provider's
pooled PostgreSQL URL in production.

### `await connect()`

Opens the connection pool and waits until its minimum number of connections is
ready. Calling it again while connected has no effect.

### `await close()`

Closes the pool and releases its connections. Calling it when already closed
has no effect.

### `await query(statement, parameters=None)`

Executes a statement, fetches every returned row, and converts each row to a
dictionary.

### `await execute(statement, parameters=None)`

Executes a statement and returns its affected row count.

## Transactions and errors

Each `query()` or `execute()` call checks out one pooled connection. A successful
operation is committed when the connection returns to the pool. If the
operation raises an exception, it is rolled back and the original exception is
propagated.

The current class treats each method call as a separate transaction. It does
not expose a transaction spanning multiple method calls.

Calling `query()` or `execute()` before `connect()` raises:

```text
RuntimeError: Database is not connected; call connect() first
```

Database connection failures and SQL errors are intentionally not hidden, so
the service or route layer can log them and translate them into an appropriate
API response.

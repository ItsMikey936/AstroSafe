"""Opens connections to the SQLite database.

The app only displays data, so the database is opened in read-only
mode: a bug in the GUI can never change or delete anything.
"""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from app import config


class DatabaseNotFoundError(FileNotFoundError):
    """Raised when neither the real nor the demo database exists."""


def get_database_path() -> Path:
    """Return the path of the database file or raise a clear error."""
    path = config.database_path()
    if not path.exists():
        raise DatabaseNotFoundError(
            f"No database found. Put '{config.DB_FILE_NAME}' inside "
            f"'{config.DATA_DIR}' or run: python scripts/create_demo_db.py"
        )
    return path


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    """Open a read-only connection and always close it afterwards.

    Usage:
        with connect() as connection:
            rows = connection.execute("SELECT ...").fetchall()
    """
    uri = get_database_path().as_uri() + "?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    # Rows behave like dictionaries: row["name"] instead of row[1].
    connection.row_factory = sqlite3.Row
    try:
        yield connection
    finally:
        connection.close()


def fetch_all(query: str, params: tuple = ()) -> list[sqlite3.Row]:
    """Run a SELECT and return every row."""
    with connect() as connection:
        return connection.execute(query, params).fetchall()


def fetch_one(query: str, params: tuple = ()) -> sqlite3.Row | None:
    """Run a SELECT and return the first row (or None)."""
    with connect() as connection:
        return connection.execute(query, params).fetchone()


if __name__ == "__main__":
    # Quick check: python -m app.backend.database
    print("Database file:", get_database_path())
    tables = fetch_all(
        "SELECT name FROM sqlite_master "
        "WHERE type IN ('table', 'view') ORDER BY name"
    )
    for table in tables:
        print(" -", table["name"])

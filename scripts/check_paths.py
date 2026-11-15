"""Report whether each image and record in the database exists."""
import sqlite3
import sys
from pathlib import Path

# Support running this file directly with python scripts/check_paths.py.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.backend.database import (  # noqa: E402
    DatabaseNotFoundError,
    fetch_all,
    get_database_path,
)
from app.backend.file_service import file_exists  # noqa: E402


_QUERY = """
    SELECT 'disease' AS source, disease_id AS item_id, image_path AS path
    FROM disease
    UNION ALL
    SELECT 'hazard', hazard_id, image_path FROM hazard
    UNION ALL
    SELECT 'treatment', treatment_id, image_path FROM treatment
    UNION ALL
    SELECT 'record', record_id, file_path FROM record
    ORDER BY source, item_id
"""


def main() -> int:
    """Print one status per reference and return 1 if any are missing."""
    try:
        print(f"Database: {get_database_path()}")
        rows = fetch_all(_QUERY)
    except (DatabaseNotFoundError, sqlite3.Error) as error:
        print(f"Cannot check database paths: {error}", file=sys.stderr)
        return 1

    if not rows:
        print("No paths found: library and record tables are empty")

    missing = 0
    for row in rows:
        exists = file_exists(row["path"])
        if not exists:
            missing += 1
        status = "OK" if exists else "MISSING"
        print(f"{status} {row['source']} {row['item_id']}: {row['path']}")

    found = len(rows) - missing
    print(f"Checked {len(rows)} paths: {found} ok, {missing} missing")
    return int(missing > 0)


if __name__ == "__main__":
    raise SystemExit(main())

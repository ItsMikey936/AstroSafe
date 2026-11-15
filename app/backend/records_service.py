"""Read record counts and files for each astronaut."""
from app import config
from app.backend.database import connect, fetch_all
from app.backend.models import AstronautRecords, RecordEntry, RecordOwner


def list_record_owners() -> list[RecordOwner]:
    """Return every astronaut with their record count, including zero."""
    rows = fetch_all(
        """
        SELECT a.astronaut_id, a.name, p.name AS position,
               COUNT(r.record_id) AS record_count
        FROM astronaut AS a
        JOIN position AS p ON p.position_id = a.position_id
        LEFT JOIN record AS r ON r.astronaut_id = a.astronaut_id
        GROUP BY a.astronaut_id, a.name, p.name
        ORDER BY a.name, a.astronaut_id
        """
    )
    return [
        RecordOwner(
            astronaut_id=row["astronaut_id"],
            name=row["name"],
            position=row["position"],
            record_count=row["record_count"],
        )
        for row in rows
    ]


def is_voice_type(record_type_name: str) -> bool:
    """Return whether the type name contains the configured voice keyword."""
    keyword = config.VOICE_RECORD_KEYWORD.casefold()
    return keyword in record_type_name.casefold()


def get_astronaut_records(astronaut_id: int) -> AstronautRecords | None:
    """Return both record groups, or None if the astronaut is absent."""
    with connect() as connection:
        person = connection.execute(
            """
            SELECT a.astronaut_id, a.name, p.name AS position
            FROM astronaut AS a
            JOIN position AS p ON p.position_id = a.position_id
            WHERE a.astronaut_id = ?
            """,
            (astronaut_id,),
        ).fetchone()
        if person is None:
            return None

        rows = connection.execute(
            """
            SELECT r.record_id, rt.name AS record_type,
                   r.record_date, r.file_path
            FROM record AS r
            JOIN record_type AS rt ON rt.record_type_id = r.record_type_id
            WHERE r.astronaut_id = ?
            ORDER BY r.record_date DESC, r.record_id DESC
            """,
            (astronaut_id,),
        ).fetchall()

    entries = [
        RecordEntry(
            record_id=row["record_id"],
            record_type=row["record_type"],
            record_date=row["record_date"],
            file_path=row["file_path"],
            is_voice=is_voice_type(row["record_type"]),
        )
        for row in rows
    ]
    return AstronautRecords(
        astronaut_id=person["astronaut_id"],
        name=person["name"],
        position=person["position"],
        voice_records=[entry for entry in entries if entry.is_voice],
        other_records=[entry for entry in entries if not entry.is_voice],
    )


if __name__ == "__main__":
    # Quick check: python -m app.backend.records_service
    owners = list_record_owners()
    print(f"{len(owners)} astronaut(s)")
    for owner in owners:
        print(owner)
    if owners:
        print(get_astronaut_records(owners[0].astronaut_id))

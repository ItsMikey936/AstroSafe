"""Crew data: astronauts, live biometrics and radiation doses.

Used by the crew general view and the crew detail screen.
"""
from app.backend.database import connect, fetch_all
from app.backend.models import (
    CrewDetail,
    CrewSummary,
    MetricValue,
    normalize_name,
)


def list_crew() -> list[CrewSummary]:
    """Every astronaut with the latest SpO2 and bpm of their watch."""
    rows = fetch_all(
        """
        SELECT a.astronaut_id,
               a.name,
               p.name AS position,
               lr.oxygenation_pct,
               lr.bpm
        FROM astronaut AS a
        JOIN position AS p ON p.position_id = a.position_id
        LEFT JOIN v_latest_reading AS lr
               ON lr.astronaut_id = a.astronaut_id
        ORDER BY a.name
        """
    )
    return [
        CrewSummary(
            astronaut_id=row["astronaut_id"],
            name=row["name"],
            position=row["position"],
            spo2=row["oxygenation_pct"],
            bpm=row["bpm"],
        )
        for row in rows
    ]


def get_crew_detail(astronaut_id: int) -> CrewDetail | None:
    """All values of the crew detail screen, or None if not found."""
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

        reading = connection.execute(
            "SELECT body_temp_c FROM v_latest_reading "
            "WHERE astronaut_id = ?",
            (astronaut_id,),
        ).fetchone()

        body = connection.execute(
            """
            SELECT muscle_mass_kg, bone_mineral_density_g_cm2
            FROM body_composition
            WHERE astronaut_id = ?
            ORDER BY measured_at DESC
            LIMIT 1
            """,
            (astronaut_id,),
        ).fetchone()

        sleep = connection.execute(
            """
            SELECT hours
            FROM sleep_log
            WHERE astronaut_id = ?
            ORDER BY sleep_date DESC
            LIMIT 1
            """,
            (astronaut_id,),
        ).fetchone()

        daily = connection.execute(
            """
            SELECT daily_dose_msv
            FROM v_daily_dose
            WHERE astronaut_id = ?
            ORDER BY day DESC
            LIMIT 1
            """,
            (astronaut_id,),
        ).fetchone()

        cumulative = connection.execute(
            """
            SELECT cumulative_dose_msv
            FROM v_cumulative_dose
            WHERE astronaut_id = ?
            ORDER BY day DESC
            LIMIT 1
            """,
            (astronaut_id,),
        ).fetchone()

        metric_rows = connection.execute(
            """
            SELECT m.name, m.unit, ms.measured_value, ms.measured_at
            FROM measurement AS ms
            JOIN metric AS m ON m.metric_id = ms.metric_id
            WHERE ms.astronaut_id = ?
              AND ms.measured_at = (
                    SELECT MAX(ms2.measured_at)
                    FROM measurement AS ms2
                    WHERE ms2.astronaut_id = ms.astronaut_id
                      AND ms2.metric_id = ms.metric_id)
            """,
            (astronaut_id,),
        ).fetchall()

    metrics = {
        normalize_name(row["name"]): MetricValue(
            name=row["name"],
            unit=row["unit"],
            value=row["measured_value"],
            measured_at=row["measured_at"],
        )
        for row in metric_rows
    }

    return CrewDetail(
        astronaut_id=person["astronaut_id"],
        name=person["name"],
        position=person["position"],
        body_temp_c=_value(reading, "body_temp_c"),
        muscle_mass_kg=_value(body, "muscle_mass_kg"),
        bone_density_g_cm2=_value(body, "bone_mineral_density_g_cm2"),
        sleep_hours=_value(sleep, "hours"),
        cumulative_dose_msv=_value(cumulative, "cumulative_dose_msv"),
        daily_dose_msv=_value(daily, "daily_dose_msv"),
        metrics=metrics,
    )


def _value(row, column: str):
    """Return row[column], or None when the query found nothing."""
    if row is None:
        return None
    return row[column]


if __name__ == "__main__":
    # Quick check: python -m app.backend.crew_service
    crew = list_crew()
    for member in crew:
        print(member)
    if crew:
        print()
        print(get_crew_detail(crew[0].astronaut_id))

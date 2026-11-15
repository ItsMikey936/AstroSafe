"""Fake crew data for the frontend tests (no database needed).

It returns the same classes as app/backend/crew_service.py, so the
tests also check that the screens follow the models.py contract.
"""
from app.backend.models import CrewDetail, CrewSummary, MetricValue

POSITIONS = ["Commander", "Pilot", "Engineer", "Doctor", "Scientist",
             "Specialist"]


class FakeCrewSource:
    """Six astronauts (ids 1-6) with fixed values."""

    def __init__(self, count: int = 6):
        self.calls = 0
        self._crew = [
            CrewSummary(astronaut_id=number, name=f"Astronaut {number}",
                        position=POSITIONS[(number - 1) % len(POSITIONS)],
                        spo2=95 + number % 4, bpm=60 + number)
            for number in range(1, count + 1)
        ]

    def list_crew(self) -> list[CrewSummary]:
        self.calls += 1
        return list(self._crew)

    def get_crew_detail(self, astronaut_id: int) -> CrewDetail | None:
        self.calls += 1
        for member in self._crew:
            if member.astronaut_id == astronaut_id:
                return _detail(member)
        return None


def _detail(member: CrewSummary) -> CrewDetail:
    metrics = {
        "intracranialpressure": MetricValue(
            "Intracranial Pressure", "mmHg", 12.0, "2026-11-15 10:00"),
        "stress": MetricValue("Stress", "/100", 10.0, "2026-11-15 10:00"),
        # No fatigue metric on purpose: the screen must show '--'.
    }
    return CrewDetail(
        astronaut_id=member.astronaut_id,
        name=member.name,
        position=member.position,
        body_temp_c=36.8,
        muscle_mass_kg=33.0,
        bone_density_g_cm2=1.25,
        sleep_hours=7.5,
        cumulative_dose_msv=15.0,
        daily_dose_msv=0.1,
        metrics=metrics,
    )

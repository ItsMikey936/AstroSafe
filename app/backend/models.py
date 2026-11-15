"""Plain data objects that the backend gives to the frontend.

The frontend never sees SQL rows, only these classes. This is the
"contract" between the two teams: as long as these fields stay the
same, each team can change its own code freely.
"""
from dataclasses import dataclass, field


def normalize_name(name: str) -> str:
    """'Intracranial Pressure' -> 'intracranialpressure'."""
    return "".join(char for char in name.lower() if char.isalnum())


# ---------------------------------------------------------------------
# Crew
# ---------------------------------------------------------------------
@dataclass(frozen=True)
class CrewSummary:
    """One card of the crew general view."""

    astronaut_id: int
    name: str
    position: str
    spo2: float | None
    bpm: int | None


@dataclass(frozen=True)
class MetricValue:
    """Latest value of a metric from the metric catalog."""

    name: str
    unit: str
    value: float
    measured_at: str


@dataclass(frozen=True)
class CrewDetail:
    """Everything shown on the crew detail screen."""

    astronaut_id: int
    name: str
    position: str
    body_temp_c: float | None
    muscle_mass_kg: float | None
    bone_density_g_cm2: float | None
    sleep_hours: float | None
    cumulative_dose_msv: float | None
    daily_dose_msv: float | None
    metrics: dict[str, MetricValue] = field(default_factory=dict)

    def metric(self, keyword: str) -> MetricValue | None:
        """Find a metric whose name contains the keyword.

        Example: detail.metric("stress") finds "Stress Level".
        """
        wanted = normalize_name(keyword)
        for key, value in self.metrics.items():
            if wanted in key:
                return value
        return None


# ---------------------------------------------------------------------
# Library (diseases, hazards, treatments)
# ---------------------------------------------------------------------
@dataclass(frozen=True)
class LibraryItem:
    """One disease, hazard or treatment."""

    item_id: int
    name: str
    description: str
    image_path: str


@dataclass(frozen=True)
class LibrarySection:
    """One of the (up to three) titled sections of an item."""

    number: int
    title: str
    description: str


@dataclass(frozen=True)
class LibraryDetail:
    """An item plus its sections (the procedure screen)."""

    item: LibraryItem
    sections: list[LibrarySection]


# ---------------------------------------------------------------------
# Records
# ---------------------------------------------------------------------
@dataclass(frozen=True)
class RecordOwner:
    """One card of the records list (an astronaut and record count)."""

    astronaut_id: int
    name: str
    position: str
    record_count: int


@dataclass(frozen=True)
class RecordEntry:
    """One record file (voice or any other type)."""

    record_id: int
    record_type: str
    record_date: str
    file_path: str
    is_voice: bool


@dataclass(frozen=True)
class AstronautRecords:
    """The records screen of one astronaut."""

    astronaut_id: int
    name: str
    position: str
    voice_records: list[RecordEntry]
    other_records: list[RecordEntry]

"""Create data/demo.db: a small fake database for testing.

Every team member can run this to test the app on their own computer
without the real database:

    python scripts/create_demo_db.py

It uses data/schema.sql (the team's schema) and fills it with made-up
data. Images and record files are generated in data/demo_files/.
"""
import random
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SCHEMA_FILE = DATA_DIR / "schema.sql"
DEMO_DB = DATA_DIR / "demo.db"
FILES_DIR = DATA_DIR / "demo_files"

READING_DAYS = 3
READING_STEP_SECONDS = 60  # the real watch sends one per second

POSITIONS = ["Commander", "Pilot", "Aerospace Engineer", "Flight Surgeon"]
ASTRONAUTS = [
    ("Ana Lucia Torres", 1),
    ("Marco Ruiz Delgado", 2),
    ("Elena Vasquez Mora", 3),
    ("Daniel Ortega Lima", 3),
    ("Sofia Herrera Cano", 4),
    ("Luis Navarro Pena", 3),
]
METRICS = [
    ("Intracranial Pressure", "mmHg", 5, 12),
    ("Stress Level", "/100", 5, 40),
    ("Fatigue Level", "/100", 5, 40),
]
RECORD_TYPES = ["Voice Record", "Medical Report", "Psychological Evaluation"]
LIBRARY = {
    "disease": [
        ("Space Motion Sickness", (220, 60, 80)),
        ("Spaceflight Osteopenia", (200, 90, 60)),
        ("Decompression Sickness", (180, 50, 120)),
    ],
    "hazard": [
        ("Cosmic Radiation", (230, 170, 40)),
        ("Microgravity", (60, 150, 220)),
        ("Isolation and Confinement", (120, 110, 200)),
    ],
    "treatment": [
        ("Resistance Exercise Protocol", (200, 30, 30)),
        ("Antiemetic Medication", (40, 170, 140)),
        ("Radiation Shelter Procedure", (90, 120, 200)),
    ],
}
SECTION_TITLES = ["Symptoms", "Procedure", "Prevention"]


def ts(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%d %H:%M:%S")


def make_image(path: Path, color: tuple) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((16, 16, 240, 240), fill=color + (255,))
    draw.ellipse((90, 90, 166, 166), fill=(255, 255, 255, 220))
    image.save(path)


def make_text_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    if not SCHEMA_FILE.exists():
        sys.exit(f"Schema not found: {SCHEMA_FILE}")
    if DEMO_DB.exists():
        DEMO_DB.unlink()

    random.seed(42)
    now = datetime.now(timezone.utc).replace(microsecond=0, tzinfo=None)
    today = now.date()
    connection = sqlite3.connect(DEMO_DB)
    connection.executescript(SCHEMA_FILE.read_text(encoding="utf-8"))
    cur = connection.cursor()

    cur.executemany(
        "INSERT INTO position (position_id, name) VALUES (?, ?)",
        list(enumerate(POSITIONS, start=1)),
    )
    cur.executemany(
        "INSERT INTO astronaut (astronaut_id, name, position_id) "
        "VALUES (?, ?, ?)",
        [(i, name, pos) for i, (name, pos) in enumerate(ASTRONAUTS, 1)],
    )
    cur.executemany(
        "INSERT INTO alert_state (state_id, name) VALUES (?, ?)",
        [(1, "Normal"), (2, "Warning"), (3, "Critical")],
    )
    cur.executemany(
        "INSERT INTO emergency_type (emergency_type_id, name) VALUES (?, ?)",
        [(1, "Radiation Exposure"), (2, "Hypoxia")],
    )
    cur.executemany(
        "INSERT INTO metric (metric_id, name, unit) VALUES (?, ?, ?)",
        [(i, m[0], m[1]) for i, m in enumerate(METRICS, start=1)],
    )
    cur.executemany(
        "INSERT INTO record_type (record_type_id, name) VALUES (?, ?)",
        list(enumerate(RECORD_TYPES, start=1)),
    )
    cur.execute(
        "INSERT INTO mission (mission_id, name, start_date) "
        "VALUES (1, 'Artemis Demo', ?)",
        ((today - timedelta(days=30)).isoformat(),),
    )

    start = now - timedelta(days=READING_DAYS)
    for astronaut_id in range(1, len(ASTRONAUTS) + 1):
        watch_id = f"W-{astronaut_id:03d}"
        cur.execute(
            "INSERT INTO mission_crew VALUES (1, ?)", (astronaut_id,)
        )
        cur.execute("INSERT INTO watch (watch_id) VALUES (?)", (watch_id,))
        cur.execute(
            "INSERT INTO watch_assignment "
            "(watch_id, astronaut_id, assigned_from) VALUES (?, ?, ?)",
            (watch_id, astronaut_id, ts(start)),
        )
        readings = []
        moment = start
        while moment <= now:
            readings.append((
                watch_id,
                ts(moment),
                random.randint(62, 88),
                round(random.uniform(95, 99.5), 1),
                round(random.uniform(36.4, 37.3), 1),
                round(random.uniform(0.00005, 0.0001), 6),
            ))
            moment += timedelta(seconds=READING_STEP_SECONDS)
        cur.executemany(
            "INSERT INTO reading VALUES (?, ?, ?, ?, ?, ?)", readings
        )

        for days_ago in range(3):
            day = today - timedelta(days=days_ago)
            cur.execute(
                "INSERT INTO sleep_log VALUES (?, ?, ?)",
                (astronaut_id, day.isoformat(),
                 round(random.uniform(5.5, 8.5), 2)),
            )
            cur.execute(
                "INSERT INTO body_composition VALUES (?, ?, ?, ?)",
                (astronaut_id, f"{day.isoformat()} 08:00:00",
                 round(random.uniform(28, 40), 1),
                 round(random.uniform(0.8, 1.2), 2)),
            )
            for metric_id, (_, _, low, high) in enumerate(METRICS, 1):
                cur.execute(
                    "INSERT INTO measurement VALUES (?, ?, ?, ?)",
                    (astronaut_id, metric_id, f"{day.isoformat()} 09:00:00",
                     random.randint(low, high)),
                )

        for number in range(1, 7):
            type_id = 1 if number <= 2 else random.choice([2, 3])
            day = today - timedelta(days=number * 3)
            extension = "txt"
            relative = (f"demo_files/records/a{astronaut_id}_"
                        f"{number}.{extension}")
            make_text_file(
                DATA_DIR / relative,
                f"{RECORD_TYPES[type_id - 1]} for astronaut "
                f"{astronaut_id} on {day.isoformat()}\n",
            )
            cur.execute(
                "INSERT INTO record (astronaut_id, record_type_id, "
                "record_date, file_path) VALUES (?, ?, ?, ?)",
                (astronaut_id, type_id, day.isoformat(), relative),
            )

    for table, items in LIBRARY.items():
        for item_id, (name, color) in enumerate(items, start=1):
            relative = f"demo_files/images/{table}_{item_id}.png"
            make_image(DATA_DIR / relative, color)
            cur.execute(
                f"INSERT INTO {table} ({table}_id, name, description, "
                f"image_path) VALUES (?, ?, ?, ?)",
                (item_id, name,
                 f"Demo description of {name.lower()}. Replace this "
                 f"text with the real information from the database.",
                 relative),
            )
            for number, title in enumerate(SECTION_TITLES, start=1):
                cur.execute(
                    f"INSERT INTO {table}_section VALUES (?, ?, ?, ?)",
                    (item_id, number, title,
                     f"{title} information for {name.lower()}."),
                )

    connection.commit()
    connection.close()
    print(f"Demo database created: {DEMO_DB}")


if __name__ == "__main__":
    main()

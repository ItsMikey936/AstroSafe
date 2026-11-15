"""Central configuration shared by the whole app.

Every path the app uses is calculated here, so the rest of the code
never has to guess where the database, the data files or the icons
live. It also works after the app is turned into an executable.
"""
import sys
from pathlib import Path

APP_NAME = "Astronaut Health Monitor"

# Name of the real database file inside the data/ folder.
DB_FILE_NAME = "astronaut_health.db"
# Demo database created by scripts/create_demo_db.py (used as fallback).
DEMO_DB_FILE_NAME = "demo.db"

# A record whose type name contains this word is shown as a voice record.
VOICE_RECORD_KEYWORD = "voice"

# How often (milliseconds) the crew screens reload the live biometrics.
REFRESH_INTERVAL_MS = 5000


def _app_root() -> Path:
    """Folder that holds the data/ folder.

    While developing it is the project folder. In the executable it is
    the folder that contains the .exe (or the Linux binary).
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def _resource_root() -> Path:
    """Folder that holds the assets/ folder (bundled inside the exe)."""
    bundle_dir = getattr(sys, "_MEIPASS", None)
    if bundle_dir:
        return Path(bundle_dir)
    return Path(__file__).resolve().parent.parent


APP_ROOT = _app_root()
DATA_DIR = APP_ROOT / "data"
ASSETS_DIR = _resource_root() / "assets"
ICONS_DIR = ASSETS_DIR / "icons"


def database_path() -> Path:
    """Return the real database if it exists, otherwise the demo one."""
    real_db = DATA_DIR / DB_FILE_NAME
    if real_db.exists():
        return real_db
    return DATA_DIR / DEMO_DB_FILE_NAME

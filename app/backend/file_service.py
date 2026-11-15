"""Resolve and open files referenced by the database."""
import os
import subprocess
import sys
from pathlib import Path, PureWindowsPath

from app import config


def resolve_path(relative_path: str) -> Path:
    """Resolve a relative file path inside data/ or raise ValueError."""
    relative = PureWindowsPath(relative_path)
    if relative.anchor or not relative.parts or "\0" in relative_path:
        raise ValueError(f"Expected a relative file path: {relative_path!r}")

    try:
        data_dir = config.DATA_DIR.resolve()
        path = (data_dir / relative.as_posix()).resolve()
    except (OSError, RuntimeError) as error:
        raise ValueError(f"Cannot resolve path: {relative_path!r}") from error

    if data_dir not in path.parents:
        raise ValueError(f"Path outside the data directory: {relative_path!r}")
    return path


def file_exists(relative_path: str) -> bool:
    """Return whether the path points to a regular file inside data/."""
    try:
        return resolve_path(relative_path).is_file()
    except (OSError, ValueError):
        return False


def open_file(relative_path: str) -> bool:
    """Request opening a file, returning False if launch is unavailable."""
    try:
        path = resolve_path(relative_path)
        if not path.is_file():
            return False

        if sys.platform == "win32":
            os.startfile(path)
        else:
            command = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.Popen([command, str(path)])
    except (OSError, ValueError):
        return False
    return True


if __name__ == "__main__":
    # Quick check: python -m app.backend.file_service
    print(f"Data directory: {config.DATA_DIR}")
    print(f"Example: {resolve_path('demo_files/images/disease_1.png')}")
    try:
        resolve_path("../secret.txt")
    except ValueError as error:
        print(f"Rejected: {error}")

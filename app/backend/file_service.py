"""Turns the relative paths stored in the database into real files.

The database stores paths like 'images/flu.png'. They are always
relative to the data/ folder, so the same database works on Windows,
on Linux and inside the final executable.
"""
import os
import subprocess
import sys
from pathlib import Path

from app import config


def resolve_path(relative_path: str) -> Path:
    """'images/flu.png' -> <project>/data/images/flu.png.

    Raises ValueError if the path tries to leave the data/ folder.
    """
    # Accept both 'a/b.png' and 'a\\b.png' (Windows style).
    clean = relative_path.strip().replace("\\", "/")
    data_dir = config.DATA_DIR.resolve()
    path = (data_dir / clean).resolve()
    if data_dir not in path.parents:
        raise ValueError(f"Path outside the data folder: {relative_path}")
    return path


def file_exists(relative_path: str) -> bool:
    """True when the relative path points to an existing file."""
    try:
        return resolve_path(relative_path).is_file()
    except ValueError:
        return False


def open_file(relative_path: str) -> None:
    """Open a file with the default program of the computer.

    Audio opens in the music player, PDFs in the PDF viewer, etc.
    Raises FileNotFoundError if the file is missing.
    """
    path = resolve_path(relative_path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    if sys.platform.startswith("win"):
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    else:
        # Linux (Arch): needs the xdg-utils package.
        subprocess.Popen(["xdg-open", str(path)])


if __name__ == "__main__":
    # Quick check: python -m app.backend.file_service
    print("Data folder:", config.DATA_DIR)
    print("Example:", resolve_path("images/example.png"))

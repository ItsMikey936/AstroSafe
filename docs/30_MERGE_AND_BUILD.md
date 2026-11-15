# 30 · Final merge and executable

## 1. Everybody: final check

When the four Pull Requests are merged:

```bash
git checkout main
git pull
python -m pip install -r requirements-dev.txt
python -m flake8 app main.py build.py scripts
python main.py
```

Go through every screen together and compare it with the prototype.
Fix small issues with a new branch (`fix/short-description`) and a PR,
same as before.

## 2. Build the Windows executable (Person 4, or anyone on Windows)

PyInstaller builds for the system it runs on: a Windows `.exe` must be
built on Windows, a Linux program on Linux.

```powershell
.\.venv\Scripts\Activate.ps1
python build.py
```

It takes a minute or two. The result is the folder
`dist\AstronautHealth\` containing:

```
AstronautHealth.exe    <- double click to start
_internal\             <- Python and the libraries (do not touch)
data\                  <- the database and its files
```

To share it, zip the **whole** `AstronautHealth` folder. To update
the data later, replace `data\astronaut_health.db` inside it; no
rebuild needed.

> Windows Defender or SmartScreen sometimes warns about new unsigned
> executables made with PyInstaller. Click "More info" > "Run anyway".

## 3. Build the Linux version (the Arch Linux teammate, optional)

```bash
source .venv/bin/activate
python build.py
./dist/AstronautHealth/AstronautHealth
```

## 4. Do not commit the build

`build/` and `dist/` are in `.gitignore` on purpose: they are large
and anyone can recreate them with `python build.py`. Share the zip
through Drive, or attach it to a GitHub Release (repository page >
Releases > Draft a new release > attach the zip).

## Common build problems

| Problem | Fix |
|---|---|
| `No module named PyInstaller` | Activate `.venv` and `pip install -r requirements-dev.txt`. |
| `No .db file in data/` | Put the database in `data/` (or run `python scripts/create_demo_db.py` for a demo build). |
| The exe opens and closes | Run it from PowerShell (`.\dist\AstronautHealth\AstronautHealth.exe`) to see the error. Usually a missing `data` folder next to it. |
| Images missing in the exe | The paths in the database must be relative to `data/` and the files must be inside `data/` before building (`python scripts/check_paths.py`). |

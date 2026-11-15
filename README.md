# Astronaut Health Monitor

A desktop app written 100% in Python that shows the health of a space
crew. It reads an SQLite database and displays it with CustomTkinter.

## Screens

| Screen | Prototype file | Code |
|---|---|---|
| Crew general view | `Tripulants_General_View.png` | `app/frontend/crew_screens.py` |
| Crew member detail | `Tripulant_View_Normal_stats.png` | `app/frontend/crew_screens.py` |
| Diseases / Hazards / Treatments list | `Informacion_Diseases.png`, `Information_Hazard.png`, `Informacion_Treatments.png` | `app/frontend/library_screens.py` |
| Disease / Hazard / Treatment detail | `Structure_Information_1.png` | `app/frontend/library_screens.py` |
| Records list | `Information_Records.png` | `app/frontend/records_screens.py` |
| Records of one astronaut | `Informacion_Records.png` | `app/frontend/records_screens.py` |

## Project structure

```
astronaut-health/
├── main.py                  <- starts the app
├── build.py                 <- creates the executable
├── requirements.txt         <- libraries the app needs
├── requirements-dev.txt     <- + tools for the team (flake8, pyinstaller)
├── app/
│   ├── config.py            <- paths and settings
│   ├── backend/             <- reads the database (no GUI code)
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── crew_service.py
│   │   ├── library_service.py
│   │   ├── records_service.py
│   │   └── file_service.py
│   └── frontend/            <- the screens (no SQL code)
│       ├── theme.py
│       ├── formatting.py
│       ├── widgets.py
│       ├── main_window.py
│       ├── crew_screens.py
│       ├── library_screens.py
│       └── records_screens.py
├── data/
│   ├── schema.sql           <- the team's database schema
│   ├── astronaut_health.db  <- the real database (you add it)
│   └── ...                  <- images and record files (relative paths)
├── assets/icons/            <- icons exported from the prototype
├── scripts/
│   ├── create_demo_db.py    <- fake database for testing
│   └── check_paths.py       <- finds missing images/records
└── docs/                    <- the team guides (start with 00)
```

## Quick start

Windows (PowerShell):

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python scripts/create_demo_db.py
python main.py
```

Arch Linux:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/create_demo_db.py
python main.py
```



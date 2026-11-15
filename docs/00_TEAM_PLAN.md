# 00 · Team plan

## How the app is organized

The app has two layers. Keeping them apart is what lets four people
work at the same time without stepping on each other.

```
 Screens (frontend)        ->  ask for data  ->   Services (backend)    ->  SQLite
 crew_screens.py                                  crew_service.py
 library_screens.py                               library_service.py
 records_screens.py                               records_service.py
                                                  file_service.py
```

The frontend never writes SQL. The backend never creates windows. They
talk through the classes in `app/backend/models.py` (for example
`CrewSummary` has `name`, `position`, `spo2`, `bpm`). That file is the
contract between the two teams.

## The teams

| Person | Team | Branch | Files they own |
|---|---|---|---|
| Person 1 | Backend (lead) | `setup/project-skeleton`, then `feature/backend-crew` | Project skeleton, `config.py`, `database.py`, `models.py`, `create_demo_db.py`, the real database, `crew_service.py` |
| Person 2 | Backend | `feature/backend-library-records` | `library_service.py`, `records_service.py`, `file_service.py`, `check_paths.py` |
| Person 3 | Frontend (lead) | `feature/frontend-shell-crew` | `theme.py`, `formatting.py`, `widgets.py`, `main_window.py`, `main.py`, `crew_screens.py`, avatar icon |
| Person 4 | Frontend | `feature/frontend-library-records` | `library_screens.py`, `records_screens.py`, `build.py`, library and record icons |

Any person can be on Windows or Arch Linux: every guide gives the
commands for both. Decide the names now and write them here:

- Person 1: ______________________
- Person 2: ______________________
- Person 3: ______________________
- Person 4: ______________________

## Golden rule

Only create or edit the files in your row. Because nobody touches
someone else's file, Git never has conflicts to resolve. If you need a
change in another person's file, ask them.

## Order of work

```
Phase 0  Person 1 creates the repository and the skeleton   (1 PR)
            |
Phase 1  Everybody works at the same time on their branch
            |
Phase 2  Merge in this order:
            1. Person 1 (crew_service)    2. Person 2 (services)
            3. Person 3 (shell + crew)    4. Person 4 (library + records)
            |
Phase 3  Build the executable (Person 4 on Windows, Linux optional)
```

Why this order? Each step only needs what was merged before it:

- Person 3's crew screens need `crew_service.py` (Person 1).
- Person 4's screens need `widgets.py` (Person 3) and Person 2's services.

Until the end, a screen whose file is not merged yet shows "This
screen is not ready yet" instead of crashing.

## Where everyone gets the code

The team lead received a package (zip) with the complete project. Each
person copies **only their own files** from that package into the
same path in their cloned repository, then commits and pushes them.
Every guide says exactly which files and where.

## Testing without the real database

`scripts/create_demo_db.py` builds `data/demo.db` with fake astronauts
from `data/schema.sql`. If the real `data/astronaut_health.db` is
missing, the app automatically uses the demo one. This way nobody
waits for anyone to start testing.

## Checklist for every person

- [ ] Followed `01_SETUP_WINDOWS.md` or `02_SETUP_ARCH_LINUX.md`
- [ ] Read `03_GIT_WORKFLOW.md`
- [ ] Created my branch
- [ ] Copied my files
- [ ] `flake8` shows no errors (PEP8)
- [ ] Ran my check command
- [ ] Pushed and opened a Pull Request

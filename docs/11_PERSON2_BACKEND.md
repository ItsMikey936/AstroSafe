# 11 · Person 2: Backend (library, records and files)

You provide the data of five screens: diseases, hazards, treatments
(list and detail) and records (list and per astronaut). You also
handle files (images and records stored as relative paths).

Before starting: finish your setup guide and wait until Person 1 says
"Phase 0 is merged".

## Step 1. Clone (if you have not yet) and branch

```bash
git checkout main
git pull
git checkout -b feature/backend-library-records
```

## Step 2. Environment and demo database

Activate your virtual environment (Windows:
`.\.venv\Scripts\Activate.ps1`, Arch: `source .venv/bin/activate`),
then:

```bash
python -m pip install -r requirements-dev.txt
python scripts/create_demo_db.py
```

## Step 3. Copy your files

| File | What it does |
|---|---|
| `app/backend/library_service.py` | `list_items(category)` and `get_item_detail(category, id)` for diseases, hazards and treatments. The three tables have the same columns, so one code serves all of them. |
| `app/backend/records_service.py` | `list_record_owners()` (each astronaut with how many records) and `get_astronaut_records(id)` (voice records separated from the rest). |
| `app/backend/file_service.py` | `resolve_path()` turns `images/flu.png` into the real path inside `data/`; `open_file()` opens a record with the computer's default program (Windows `os.startfile`, Linux `xdg-open`). |
| `scripts/check_paths.py` | Lists every image/record path in the database and says if the file exists. |

Folders already exist (Person 1 created them), so just add the files.

## Step 4. Check them

```bash
python -m app.backend.library_service
python -m app.backend.records_service
python -m app.backend.file_service
python scripts/check_paths.py
python -m flake8 app scripts
```

The first two print data. `check_paths.py` must end with
`0 missing`. If something is MISSING with the real database, the file
is not in the right folder inside `data/`: tell Person 1.

### Something to learn from this code

`library_service.py` builds table names into the SQL with f-strings,
which is normally dangerous (SQL injection). It is safe here because
the names only come from the fixed `_TABLES` dictionary, never from
the user. Values (like the id) always use `?` placeholders.

## Step 5. Commit, push, Pull Request

```bash
git add app/backend/library_service.py app/backend/records_service.py
git add app/backend/file_service.py scripts/check_paths.py
git commit -m "Add library, records and file services"
git push -u origin feature/backend-library-records
```

Open the PR, ask Person 1 to review it, and merge it right after
Person 1's crew service (#2 in the merge order).

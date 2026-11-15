# 21 · Person 4: Frontend (library and records screens, final build)

You build five screens and, at the end, the executable.

| Screen | Prototype |
|---|---|
| Diseases list | `Informacion_Diseases.png` |
| Hazards list | `Information_Hazard.png` |
| Treatments list | `Informacion_Treatments.png` |
| Detail of a disease/hazard/treatment | `Structure_Information_1.png` |
| Records list | `Information_Records.png` |
| Records of one astronaut | `Informacion_Records.png` |

Before starting: finish your setup guide and wait for Phase 0.

## Step 1. Branch

```bash
git checkout main
git pull
git checkout -b feature/frontend-library-records
```

## Step 2. Copy your files

| File | What it does |
|---|---|
| `app/frontend/library_screens.py` | `LibraryListScreen` shows one big card per item (one class serves diseases, hazards and treatments). `LibraryDetailScreen` shows the round image, title, description and the three sections. |
| `app/frontend/records_screens.py` | `RecordsListScreen` shows one card per astronaut with their record count. `AstronautRecordsScreen` shows the profile with voice records on the left and the other records on the right; clicking a date opens the file. |
| `build.py` | Creates the executable at the end (see `30_MERGE_AND_BUILD.md`). |

### How the pieces fit

- Your screens inherit from `Screen` and use `ListCard`, `ProfilePanel`
  and `MessageView` from Person 3's `widgets.py`.
- They get data from Person 2's services: they never write SQL.
- Images from the database go through `file_service.resolve_path`, so
  `images/flu.png` becomes `data/images/flu.png`.
- If a record file is missing, a pop-up explains it instead of
  crashing.

## Step 3. Icons from the prototype (optional)

Export these icons as PNGs with transparent backgrounds into
`assets/icons/`:

| File | Prototype icon |
|---|---|
| `diseases.png` | The red virus |
| `hazards.png` | The hazard icon |
| `treatments.png` | The red heart |
| `records.png` | The clipboard |
| `app.ico` | Optional: icon of the Windows executable |

If an icon is missing, the list shows each item's own image from the
database, or a drawn placeholder.

## Step 4. Run it

You need Person 2's services and Person 3's widgets. When both are
merged:

```bash
git pull origin main
python main.py
```

Click Diseases, Hazards, Treatments and Records and open some items.

## Step 5. PEP8 and commit

```bash
python -m flake8 app main.py build.py
git add app/frontend/library_screens.py app/frontend/records_screens.py
git add build.py assets/icons
git commit -m "Add library and records screens and build script"
git push -u origin feature/frontend-library-records
```

Open the PR, ask Person 3 to review it, and merge it last (#4). Then
follow `30_MERGE_AND_BUILD.md`.

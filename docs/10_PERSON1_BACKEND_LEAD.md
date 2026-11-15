# 10 · Person 1: Backend lead

You have two jobs:

1. **Phase 0**: create the GitHub repository and the project skeleton
   that everybody else builds on. Nobody can start until you finish
   this, so do it first.
2. **Phase 1**: the crew service (data of the two crew screens).

Before starting, finish `01_SETUP_WINDOWS.md` or
`02_SETUP_ARCH_LINUX.md` up to step 4.

---

## Phase 0: repository and skeleton

### Step 1. Create the repository on GitHub

1. On https://github.com click **+** (top right) > **New repository**.
2. Name: `astronaut-health`. Visibility: Private (or as your teacher
   asks). Tick **Add a README file**. Click **Create repository**.
3. Settings > Collaborators > **Add people**: add the three
   teammates. They must accept the email invitation.

### Step 2. Clone it

Windows:

```powershell
cd $HOME\Documents
git clone https://github.com/YOUR_USER/astronaut-health.git
cd astronaut-health
```

Arch Linux:

```bash
mkdir -p ~/projects && cd ~/projects
git clone https://github.com/YOUR_USER/astronaut-health.git
cd astronaut-health
```

### Step 3. Create the skeleton branch

```bash
git checkout -b setup/project-skeleton
```

### Step 4. Create the folders

Windows:

```powershell
mkdir app\backend, app\frontend, data, assets\icons, scripts, docs
```

Arch Linux:

```bash
mkdir -p app/backend app/frontend data assets/icons scripts docs
```

### Step 5. Copy the skeleton files from the package

Copy each file to the same path (replace the README GitHub created):

| File | What it is |
|---|---|
| `.gitignore` | Tells Git which files never to upload (`.venv`, caches, builds, demo data) |
| `README.md` | Project overview |
| `requirements.txt` | Libraries the app needs |
| `requirements-dev.txt` | Same + flake8 and pyinstaller |
| `app/__init__.py` | Marks `app` as a Python package |
| `app/config.py` | Every path and setting in one place |
| `app/backend/__init__.py` | Marks `backend` as a package |
| `app/backend/database.py` | Opens the database (read-only) |
| `app/backend/models.py` | The data classes both teams agree on |
| `app/frontend/__init__.py` | Marks `frontend` as a package |
| `data/schema.sql` | Your schema (the `bdsqueme.txt` file) |
| `assets/icons/.gitkeep` | Empty file so Git keeps the empty folder |
| `scripts/create_demo_db.py` | Builds a fake database for testing |
| `docs/*.md` | All the guides |

> Files whose name starts with a dot (`.gitignore`, `.gitkeep`) are
> easiest to create from VS Code: New File > type the full name.

`database.py` and `models.py` go in Phase 0 (not in your feature
branch) because Person 2 needs them from day one.

### Step 6. Add the real database

1. Copy your database file to `data/astronaut_health.db` (exactly this
   name, or change `DB_FILE_NAME` in `app/config.py`).
2. The database stores image and record paths **relative to the
   `data/` folder**. If a disease has `image_path = 'images/flu.png'`,
   the file must be at `data/images/flu.png`. Copy all the images and
   record files into `data/` keeping their folders.
3. Size check: GitHub rejects files over 100 MB. If the `.db` is
   bigger (the watch saves one reading per second), share it through
   Drive instead and add the line `data/astronaut_health.db` to
   `.gitignore`. Everybody can still test with the demo database.

### Step 7. Set up your environment and test

Do steps 6 and 7 of your setup guide (virtual environment and
libraries), then:

```bash
python scripts/create_demo_db.py
python -m app.backend.database
python -m flake8 app scripts
```

You should see the list of tables (from the real database if it is
in `data/`, otherwise from `demo.db`) and no flake8 output.

### Step 8. Commit, push and merge

```bash
git status
git add .gitignore README.md requirements.txt requirements-dev.txt
git add app data/schema.sql assets scripts docs
git add data/astronaut_health.db
git commit -m "Add project skeleton, configuration and database access"
git push -u origin setup/project-skeleton
```

(Skip the `git add data/...db` line if the database is too big; also
`git add` the folders with your images and records inside `data/`.)

Open the Pull Request on GitHub and merge it yourself (this one does
not need a review). Then tell the team: **"Phase 0 is merged, you can
clone now."**

---

## Phase 1: crew service

### Step 9. Update and branch

```bash
git checkout main
git pull
git checkout -b feature/backend-crew
```

### Step 10. Copy your file

| File | What it does |
|---|---|
| `app/backend/crew_service.py` | `list_crew()` returns every astronaut with the latest SpO2 and bpm (crew general view). `get_crew_detail(id)` returns temperature, intracranial pressure, muscle mass, bone density, stress, fatigue, sleep and the radiation doses (crew detail view). |

How it uses your schema:

- SpO2, bpm and temperature come from the view `v_latest_reading`.
- Muscle mass and bone density: newest row of `body_composition`.
- Sleep: newest row of `sleep_log`.
- Daily dose: newest day of `v_daily_dose`; cumulative dose: newest
  day of `v_cumulative_dose`.
- Intracranial pressure, stress and fatigue: newest value of each
  metric in `measurement`, with name and unit from `metric`.

### Step 11. Check it

```bash
python -m app.backend.crew_service
python -m flake8 app
```

It prints every astronaut and the detail of the first one. Look at
the `metrics={...}` part: the crew screen finds metrics by the words
`intracranial`, `stress` and `fatigue`. If your catalog uses other
names (for example in Spanish), tell Person 3 so they change the
words in `crew_screens.py` (method `_show_values`).

Also check your record types: a type is shown as a voice record when
its name contains `voice`. If yours is called something else, change
`VOICE_RECORD_KEYWORD` in `app/config.py` (your file) and include it
in this commit.

### Step 12. Commit, push, Pull Request

```bash
git add app/backend/crew_service.py
git commit -m "Add crew service for crew list and crew detail screens"
git push -u origin feature/backend-crew
```

Open the PR, ask Person 2 to review, and merge it first (you are #1 in
the merge order).

### Your role during the merge

As lead, you help others if Git gives them trouble and you check that
the merge order in `00_TEAM_PLAN.md` is respected.

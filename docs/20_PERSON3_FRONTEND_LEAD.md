# 20 · Person 3: Frontend lead (window, shared widgets, crew screens)

You build the base of the GUI that every screen uses (colors, top
navigation bar, cards, stat tiles, dose rings) plus the two crew
screens.

GUI library: **CustomTkinter**, a modern-looking version of Python's
built-in Tkinter. It supports rounded corners and a dark theme like
the prototype.

Before starting: finish your setup guide and wait for Phase 0.

## Step 1. Branch

```bash
git checkout main
git pull
git checkout -b feature/frontend-shell-crew
```

Activate your virtual environment and create the demo database:

```bash
python scripts/create_demo_db.py
```

## Step 2. Copy your files

| File | What it does |
|---|---|
| `app/frontend/theme.py` | Colors and sizes taken from the prototype (navy background `#111a2c`, card `#1e2d45`, teal buttons `#22566a`...). Change a color here and it changes everywhere. |
| `app/frontend/formatting.py` | Turns numbers into text: `37.2 °C`, `10/100`, `7:30 hr`, `--` when there is no data. |
| `app/frontend/widgets.py` | Shared pieces: `NavBar`, `Screen` (base class with auto refresh), `ClickableCard`, `ListCard`, `StatPanel`, `DoseRing`, `ProfilePanel`, image loading with drawn placeholders. |
| `app/frontend/main_window.py` | The window: navigation bar on top, one screen below, and the `open_...` methods every screen uses to navigate. |
| `main.py` | Starts the app. |
| `app/frontend/crew_screens.py` | `CrewListScreen` (cards with SpO2 and bpm, prototype "Tripulants_General_View") and `CrewDetailScreen` (all stats, prototype "Tripulant_View_Normal_stats"). |

### How the pieces fit

- The prototype had no button to return to the crew list, so the
  navigation bar has an extra **Crew** button, and detail screens have
  a small "Back" link.
- Clicking a crew card opens that astronaut's detail.
- Both crew screens reload their values every 5 seconds
  (`REFRESH_INTERVAL_MS` in `app/config.py`) because the watch sends
  new readings constantly. The cards are updated, not rebuilt, so
  nothing flickers.
- The circles in the detail screen are `DoseRing` widgets.

## Step 3. Icons from the prototype (optional but nicer)

Export the person silhouette from your design tool as a PNG with a
transparent background and save it as `assets/icons/avatar.png`. If
the file does not exist, the app draws a similar silhouette itself.

## Step 4. Run it

Person 1's crew service must be merged first. Bring it into your
branch:

```bash
git pull origin main
python main.py
```

You should see the crew cards. Click one to see the detail. The
Diseases, Hazards and Records buttons show "This screen is not ready
yet" until Person 4 merges: that is expected.

If the metric names of your database are not in English, open
`crew_screens.py`, find `_show_values` and change the words
`"intracranial"`, `"stress"` and `"fatigue"` to words contained in
your metric names (Person 1 will tell you).

## Step 5. PEP8 and commit

```bash
python -m flake8 app main.py
git add app/frontend/theme.py app/frontend/formatting.py
git add app/frontend/widgets.py app/frontend/main_window.py
git add app/frontend/crew_screens.py main.py
git add assets/icons/avatar.png
git commit -m "Add main window, shared widgets and crew screens"
git push -u origin feature/frontend-shell-crew
```

(Skip the `avatar.png` line if you did not export one.)

Open the PR, ask Person 4 to review it, and merge it third. Then tell
Person 4: "widgets are in main".

## Ideas if you finish early

- Color the dose rings or the bpm badge by alert state using the
  `threshold` table (ask Person 1 for a service function).
- Show a small "updated at HH:MM:SS" label on the crew screens.

# 02 · Setup on Arch Linux

Do this once. Every command goes in a terminal.

## 1. Install the system packages

```bash
sudo pacman -Syu
sudo pacman -S --needed python tk git github-cli xdg-utils code
```

What each one is:

- `python`: Python itself.
- `tk`: the graphics toolkit that CustomTkinter draws with. Without
  it you get `ModuleNotFoundError: No module named 'tkinter'`.
- `git`: version control.
- `github-cli`: the `gh` command, the easiest way to log in to GitHub.
- `xdg-utils`: lets the app open record files in your default program.
- `code`: Visual Studio Code (open source build).

Check:

```bash
python --version
python -c "import tkinter; print('tkinter ok')"
git --version
```

## 2. Configure Git

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global pull.rebase false
git config --global init.defaultBranch main
```

## 3. Log in to GitHub

Create an account at https://github.com if needed and send your
username to Person 1. Then:

```bash
gh auth login
```

Answer: `GitHub.com` > `HTTPS` > `Yes` (authenticate Git) >
`Login with a web browser`. Copy the code it shows, press Enter and
paste it in the browser. Then:

```bash
gh auth setup-git
```

## 4. Install the VS Code extensions

Open VS Code (`code`), go to Extensions and install **Python** and
**Flake8**. If you do not find them in Code-OSS, install them from
https://open-vsx.org or use any editor you like.

## 5. Get the project

After Person 1 finishes Phase 0 and you accept the invitation:

```bash
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/OWNER/astronaut-health.git
cd astronaut-health
```

## 6. Create the virtual environment

Arch does not allow `pip install` outside a virtual environment
("externally-managed-environment" error), so this step is required.

```bash
python -m venv .venv
source .venv/bin/activate
```

If your shell is **fish**, use `source .venv/bin/activate.fish`.
The prompt now starts with `(.venv)`. **Activate it every time you
open a new terminal to work on the project.**

## 7. Install the libraries

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

### If the install fails

Arch ships the newest Python, and very rarely a library has not
published files for it yet. In that case use `uv` to create the
environment with Python 3.12 instead:

```bash
sudo pacman -S uv
rm -rf .venv
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install -r requirements-dev.txt
```

## 8. Open the project

```bash
code .
```

`Ctrl+Shift+P` > `Python: Select Interpreter` > choose `.venv`.

## 9. Test that everything works

```bash
python scripts/create_demo_db.py
python -m app.backend.database
```

## Useful Linux commands

| What | Command |
|---|---|
| Show where you are | `pwd` |
| List files | `ls -la` |
| Enter a folder | `cd folder` |
| Create folders | `mkdir -p app/backend` |
| Activate the environment | `source .venv/bin/activate` |
| Leave the environment | `deactivate` |

Paths: Windows guides write `app\backend`, on Linux it is
`app/backend`. Python commands like `python main.py` are the same.

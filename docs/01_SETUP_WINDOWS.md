# 01 · Setup on Windows

Do this once. It takes about 30 minutes. Every command goes in
**PowerShell** (press the Windows key, type `PowerShell`, press Enter).

## 1. Install Python

1. Go to https://www.python.org/downloads/windows/ and download the
   latest **Python 3.12** (or 3.13) "Windows installer (64-bit)".
2. Open the installer. On the first screen **tick "Add python.exe to
   PATH"**, then click "Install Now".
3. Close PowerShell, open a new one and check:

   ```powershell
   py --version
   ```

   You should see `Python 3.12.x` (or 3.13.x).

> If typing `python` opens the Microsoft Store: Windows Settings >
> Apps > Advanced app settings > App execution aliases, and turn off
> the two "python" aliases.

## 2. Install Git

1. Download Git from https://git-scm.com/download/win and install it.
   Keep every default option (just click Next).
2. Open a new PowerShell and check:

   ```powershell
   git --version
   ```

3. Tell Git who you are (use the email of your GitHub account):

   ```powershell
   git config --global user.name "Your Name"
   git config --global user.email "you@example.com"
   git config --global pull.rebase false
   git config --global init.defaultBranch main
   ```

## 3. Create a GitHub account

Go to https://github.com and sign up if you do not have an account.
Send your username to Person 1 so they can invite you.

## 4. Install Visual Studio Code

1. Download it from https://code.visualstudio.com and install it. On
   the "Select Additional Tasks" screen tick "Add to PATH".
2. Open VS Code > Extensions (the four squares icon on the left) and
   install **Python** (by Microsoft) and **Flake8** (by Microsoft).

## 5. Get the project

Person 1 does Phase 0 first (see `10_PERSON1_BACKEND_LEAD.md`). After
you accept the GitHub invitation (check your email):

```powershell
cd $HOME\Documents
git clone https://github.com/OWNER/astronaut-health.git
cd astronaut-health
```

Replace `OWNER` with Person 1's GitHub username. The first time Git
talks to GitHub, a browser window asks you to sign in: sign in and
authorize "Git Credential Manager".

## 6. Create the virtual environment

A virtual environment is a private folder (`.venv`) with the libraries
of this project only. Every person creates their own; it is never
pushed to GitHub (`.gitignore` excludes it).

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If you get "running scripts is disabled on this system", run this
once, answer `Y`, and activate again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

When it works, the prompt starts with `(.venv)`. **Activate it every
time you open a new PowerShell to work on the project.**

## 7. Install the libraries

With `(.venv)` visible:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

This installs `customtkinter` (GUI), `Pillow` (images), `flake8`
(PEP8 checker) and `pyinstaller` (executable builder).

## 8. Open the project in VS Code

```powershell
code .
```

Press `Ctrl+Shift+P`, type `Python: Select Interpreter` and choose
the one that says `.venv`. Now VS Code's terminal (``Ctrl+` `` or `Ctrl+ñ` on a Spanish keyboard, or
View > Terminal) opens with the environment already active.

## 9. Test that everything works

Once Phase 0 is merged:

```powershell
python scripts/create_demo_db.py
python -m app.backend.database
```

You should see "Demo database created" and a list of tables.
`python main.py` will open the window once the frontend is merged.

## Useful Windows commands

| What | Command |
|---|---|
| Show where you are | `pwd` |
| List files | `ls` |
| Enter a folder | `cd folder` |
| Go up one folder | `cd ..` |
| Create folders | `mkdir app\backend` |
| Activate the environment | `.\.venv\Scripts\Activate.ps1` |
| Leave the environment | `deactivate` |

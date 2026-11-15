# 03 · Git workflow (for people who never used Git)

## Five words you need

- **Repository (repo)**: the project folder, with its full history.
  There is one copy on GitHub and one copy on each computer.
- **Branch**: your own parallel version of the project. You work on
  your branch; `main` stays clean until your work is reviewed.
- **Commit**: a saved snapshot of your changes, with a message.
- **Push**: send your commits from your computer to GitHub.
- **Pull Request (PR)**: asking the team to merge your branch into
  `main` on GitHub.

## The whole cycle

Commands are the same on Windows (PowerShell) and Linux. Run them
inside the project folder.

### 1. Start from an updated main

```bash
git checkout main
git pull
```

### 2. Create your branch (only once)

```bash
git checkout -b feature/your-branch-name
```

Use the branch name from `00_TEAM_PLAN.md`. Check where you are:

```bash
git branch
```

The branch with `*` is the active one.

### 3. Create your folders and files

Copy your files from the package into the same path. Example for a
file `app/backend/crew_service.py`:

- In VS Code: right click the `app/backend` folder > New File >
  type `crew_service.py`, then paste the content and save
  (`Ctrl+S`).
- Or copy the file with the file explorer.

### 4. Check PEP8 and that it runs

```bash
python -m flake8 app main.py build.py scripts
```

No output means no PEP8 errors. Then run the check command of your
personal guide.

### 5. See what changed

```bash
git status
```

Red files are changed but not staged yet.

### 6. Stage and commit

```bash
git add app/backend/crew_service.py
git commit -m "Add crew service (crew list and crew detail data)"
```

Add files by name so you never commit someone else's file by
accident. Commit messages: short, start with a verb, say what it does.

### 7. Push

The first push of a branch:

```bash
git push -u origin feature/your-branch-name
```

Later pushes on the same branch are just `git push`.

### 8. Open a Pull Request

1. Open the repository on GitHub. A yellow bar says "your branch had
   recent pushes": click **Compare & pull request**.
2. Check that it says `base: main` <- `compare: your-branch`.
3. Title: what you did. Description: the files you added.
4. Click **Create pull request**.
5. Ask one teammate to review: they open the PR, tab "Files changed",
   and click **Review changes** > **Approve**.
6. When it is your turn in the merge order, click **Merge pull
   request** > **Confirm merge** > **Delete branch**.

### 9. After a merge: everybody updates

```bash
git checkout main
git pull
```

If you are still working on your branch and need the new code from
`main` (for example Person 4 needs Person 3's widgets):

```bash
git checkout feature/your-branch-name
git pull origin main
```

If an editor opens asking for a merge message, save and close it (in
the `vim` editor type `:wq` and press Enter).

## If something goes wrong

| Problem | What to do |
|---|---|
| `error: pathspec ... did not match` | You misspelled the file or branch name. Check with `git status` / `git branch`. |
| You committed on `main` by mistake | Ask Person 1 before pushing. Do not push. |
| `rejected ... fetch first` when pushing | Run `git pull`, then `git push` again. |
| `CONFLICT` | Someone edited your file (breaking the golden rule). Do not panic: tell the team, open the file, keep the right version between `<<<<<<<` and `>>>>>>>`, delete the markers, then `git add file` and `git commit`. |
| `fatal: not a git repository` | You are in the wrong folder. `cd` into `astronaut-health`. |

## PEP8 in 30 seconds

PEP8 is Python's style guide. The provided code already follows it.
The rules you will notice most:

- 4 spaces per indentation level (never tabs).
- Lines of 79 characters at most.
- `snake_case` for variables and functions, `CapWords` for classes,
  `UPPER_CASE` for constants.
- Two blank lines between top-level functions and classes.
- Imports at the top: standard library, then third party, then ours.

`python -m flake8 ...` checks all of this for you.

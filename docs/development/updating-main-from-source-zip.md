# Updating `main` from a prepared source ZIP

A source ZIP does not contain the repository's `.git` history. If you run `git init`, commit the ZIP and immediately push to an existing GitHub `main`, GitHub correctly rejects the push because the histories are unrelated.

The safest direct-from-ZIP method is to make the new commit **a child of the current remote `main` while keeping the ZIP working tree unchanged**.

From the extracted ZIP directory in PowerShell:

```powershell
git init
git remote add origin https://github.com/Cavanshirpro/YoungLionPythonLibrary.git
git fetch origin main

# Move HEAD to the current remote commit but intentionally keep the ZIP's
# index/working tree. Remote-only files become deletions; ZIP files become
# additions/modifications in the next commit.
git reset --soft origin/main

git add -A
git status
git diff --cached --check

git commit -m "chore: finalize YoungLion v0.1 pre-release source"
git branch -M main
git push -u origin main
```

If `origin` already exists, replace the `git remote add` line with:

```powershell
git remote set-url origin https://github.com/Cavanshirpro/YoungLionPythonLibrary.git
```

This does **not** force-push and does not erase previous Git history. The new commit has the current remote `main` as its parent while its tree matches the extracted ZIP.

Before pushing, `git status` should show the legacy workflow `.github/workflows/younglion-ci.yml` as deleted if it still exists in remote `main`. That deletion is intentional for v0.1 because the old workflow contained obsolete automatic release logic.

# How to publish this repo to GitHub (private)

The local repo is staged and committed. To put it on GitHub as the org's
source of truth, do these four steps once:

## 1. Create a GitHub account (if you don't have one)

Go to <https://github.com/signup> and create your account using
`mattsivley6@gmail.com` (or a Centric work email if you have one).
Verify your email.

## 2. Install GitHub CLI

Open **PowerShell** and run:

```powershell
winget install --id GitHub.cli -e
```

Close and reopen PowerShell so `gh` lands on PATH.

## 3. Authenticate

```powershell
gh auth login
```

Pick:
- **GitHub.com**
- **HTTPS**
- **Login with a web browser** (it'll open your browser, paste the one-time code)

## 4. Create the private repo and push

From this folder:

```powershell
cd "C:\Users\matts\Documents\Centric\pmi-templates"
gh repo create pmi-templates --private --source=. --remote=origin --push
```

That's it. The repo will be visible at `https://github.com/<your-username>/pmi-templates`.

---

## Day-to-day workflow

To update a template:

```powershell
# 1. Edit scripts\build_templates.py
# 2. Regenerate the .docx files
python scripts\build_templates.py

# 3. Commit and push
git add -A
git commit -m "Describe the change"
git push
```

To invite collaborators (read or write):

```powershell
gh repo edit --add-collaborator <github-username>
```

Or via the web UI: Settings -> Collaborators.

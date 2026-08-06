# How to Push All Files to GitHub

Your PakistanLawApp code is on the VPS at `/var/www/pakistanlawapp` with **510 files** ready to push.

## Quick Push (Recommended)

### Step 1: Get a GitHub Token

1. Go to https://github.com/settings/tokens
2. Click **"Generate new token (classic)"**
3. Check the **"repo"** checkbox (full control of repositories)
4. Click **"Generate token"**
5. Copy the token (starts with `ghp_`)

### Step 2: SSH to VPS and Run

```bash
ssh root@203.161.38.75
# Password: B01P2Lwm8oijr4H3QJ

cd /var/www/pakistanlawapp
bash save-to-github.sh ghp_xxxxxxxxxxxx
```

This pushes all 510 files to the `full-upload` branch in one go.

### Step 3: Merge to Main

Go to https://github.com/tnvcollection1/PakistanLawApp/pulls and merge the pull request.

## Alternative: Python Script

```bash
cd /var/www/pakistanlawapp
python3 push_all_to_github.py ghp_xxxxxxxxxxxx
```

This pushes files in batches of 20 using the GitHub API.

## Alternative: Manual Git Push

```bash
ssh root@203.161.38.75
cd /var/www/pakistanlawapp

# Configure git with token
git config --global credential.helper store
echo "https://tnvcollection1:ghp_xxxxxxxxxxxx@github.com" > ~/.git-credentials
chmod 600 ~/.git-credentials

# Push
git remote set-url origin https://tnvcollection1:ghp_xxxxxxxxxxxx@github.com/tnvcollection1/PakistanLawApp.git
git push --force origin main:full-upload

# Cleanup
rm ~/.git-credentials
```

## What Gets Pushed

- **Backend**: FastAPI server, 50+ route modules, models, database, auth
- **Frontend**: React SPA, 50+ components, 60+ pages, hooks, context
- **Scrapers**: 20+ case law scrapers
- **Config**: Docker, Nginx, PM2, environment templates
- **Scripts**: Deployment, OpenClaw installer, data cleaning

## Already on GitHub

These files have real content already:
- `README.md` — Full documentation
- `requirements.txt` — All Python dependencies
- `server.py` — FastAPI main app
- `models.py` — Pydantic models
- `database.py` — MongoDB connection
- `auth_utils.py` — JWT + bcrypt auth
- `push_all_to_github.py` — Python pusher script
- `save-to-github.sh` — Bash pusher script

## Repo Link

https://github.com/tnvcollection1/PakistanLawApp

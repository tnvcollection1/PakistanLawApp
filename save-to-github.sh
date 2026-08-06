#!/bin/bash
# save-to-github.sh — One-command push of all 510 files to GitHub
# Run this ON THE VPS with your GitHub Personal Access Token

set -e

TOKEN="${1:-}"
if [ -z "$TOKEN" ]; then
    echo "=== PakistanLawApp GitHub Push ==="
    echo ""
    echo "Usage: bash save-to-github.sh <GITHUB_TOKEN>"
    echo ""
    echo "How to get a GitHub token:"
    echo "  1. Go to https://github.com/settings/tokens"
    echo "  2. Click 'Generate new token (classic)'"
    echo "  3. Check the 'repo' checkbox (full control of repositories)"
    echo "  4. Click 'Generate token' at the bottom"
    echo "  5. Copy the token (starts with ghp_xxxx)"
    echo "  6. Run: bash save-to-github.sh ghp_xxxxxxxxxxxx"
    echo ""
    exit 1
fi

cd /var/www/pakistanlawapp

echo "Configuring git..."
git config --global credential.helper store
echo "https://tnvcollection1:${TOKEN}@github.com" > ~/.git-credentials
chmod 600 ~/.git-credentials

echo "Setting remote URL..."
git remote set-url origin "https://tnvcollection1:${TOKEN}@github.com/tnvcollection1/PakistanLawApp.git"

echo "Checking git status..."
git status --short | head -20
TOTAL=$(git status --short | wc -l)
echo "Files to push: ${TOTAL}"

echo ""
echo "Force pushing to full-upload branch..."
git push --force origin main:full-upload

echo ""
echo "Creating pull request..."
curl -s -X POST \
    -H "Authorization: token ${TOKEN}" \
    -H "Accept: application/vnd.github.v3+json" \
    https://api.github.com/repos/tnvcollection1/PakistanLawApp/pulls \
    -d '{
        "title": "Complete project sync from VPS",
        "head": "full-upload",
        "base": "main",
        "body": "Complete sync of all project files from production VPS. Includes 510+ files with full backend, frontend, routes, and configuration."
    }'

echo ""
echo "Cleaning up credentials..."
rm -f ~/.git-credentials
git config --global --unset credential.helper 2>/dev/null || true

echo ""
echo "=== DONE ==="
echo "Check: https://github.com/tnvcollection1/PakistanLawApp/tree/full-upload"

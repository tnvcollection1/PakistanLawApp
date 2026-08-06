#!/bin/bash
# push-to-github.sh — Push all committed files from VPS to GitHub
# Run this on the VPS with a GitHub Personal Access Token

set -e

echo "=== PakistanLawApp Git Push Helper ==="
echo ""

# Check if token is provided
TOKEN="${1:-}"
if [ -z "$TOKEN" ]; then
    echo "Usage: ./push-to-github.sh <GITHUB_TOKEN>"
    echo ""
    echo "To get a token:"
    echo "  1. Go to https://github.com/settings/tokens"
    echo "  2. Click 'Generate new token (classic)'"
    echo "  3. Select 'repo' scope (full control of repositories)"
    echo "  4. Generate and copy the token"
    echo "  5. Run: ./push-to-github.sh ghp_xxxxxxxxxxxx"
    echo ""
    exit 1
fi

cd /var/www/pakistanlawapp

echo "Configuring git credentials..."
git config --global credential.helper store
echo "https://tnvcollection1:${TOKEN}@github.com" > ~/.git-credentials
chmod 600 ~/.git-credentials

echo "Setting remote URL with token..."
git remote set-url origin "https://tnvcollection1:${TOKEN}@github.com/tnvcollection1/PakistanLawApp.git"

echo "Checking status..."
git status --short | head -20

echo ""
echo "Force pushing to GitHub (full-upload branch)..."
git push --force origin main:full-upload

echo ""
echo "Creating PR from full-upload to main..."
curl -s -X POST \
    -H "Authorization: token ${TOKEN}" \
    -H "Accept: application/vnd.github.v3+json" \
    https://api.github.com/repos/tnvcollection1/PakistanLawApp/pulls \
    -d '{"title":"Full project sync from VPS","head":"full-upload","base":"main","body":"Complete sync of all 510 files from production VPS."}'

echo ""
echo "=== Done! Check https://github.com/tnvcollection1/PakistanLawApp ==="

# Cleanup credential helper
git config --global --unset credential.helper 2>/dev/null || true
rm -f ~/.git-credentials

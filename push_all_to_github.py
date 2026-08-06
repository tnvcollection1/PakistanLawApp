#!/usr/bin/env python3
"""
PakistanLawApp GitHub Pusher - Push all 510 files to GitHub
Usage: python3 push_all_to_github.py <GITHUB_TOKEN>
Or: GITHUB_TOKEN=xxx python3 push_all_to_github.py
"""
import os, sys, json, time, urllib.request
from pathlib import Path

TOKEN = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GITHUB_TOKEN")
if not TOKEN:
    print("Usage: python3 push_all_to_github.py <GITHUB_TOKEN>")
    print("Get token: https://github.com/settings/tokens -> Generate new token (classic) -> repo scope")
    sys.exit(1)

OWNER = "tnvcollection1"
REPO = "PakistanLawApp"
BRANCH = "full-upload"
BASE_DIR = "/var/www/pakistanlawapp"  # Run this on VPS

def api_call(method, path, data=None):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}{path}"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "PakistanLawApp-Pusher/1.0"
    }
    if data:
        data = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        res = urllib.request.urlopen(req, timeout=30)
        return json.loads(res.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  HTTP {e.code}: {body[:200]}")
        return None

# Get current branch
print("Getting branch info...")
ref = api_call("GET", f"/git/refs/heads/{BRANCH}")
if not ref:
    print("Failed to get branch. Check token and branch name.")
    sys.exit(1)
base_sha = ref["object"]["sha"]
print(f"Base commit: {base_sha[:8]}")

# Get all tracked files
import subprocess
result = subprocess.run(["git", "ls-files"], cwd=BASE_DIR, capture_output=True, text=True)
all_files = result.stdout.strip().split("\n")
print(f"Total tracked files: {len(all_files)}")

# Filter out large/binary files
files_to_push = []
for f in all_files:
    full = os.path.join(BASE_DIR, f)
    size = os.path.getsize(full)
    if size > 300000:
        print(f"  Skip (large): {f} ({size} bytes)")
        continue
    if any(f.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.pdf', '.ico', '.woff', '.woff2', '.ttf', '.eot', '.map', '.lock', '.zip', '.tar', '.gz']):
        print(f"  Skip (binary): {f}")
        continue
    files_to_push.append((f, full, size))

print(f"\nFiles to push: {len(files_to_push)}")

# Push in batches
BATCH = 25
batches = [files_to_push[i:i+BATCH] for i in range(0, len(files_to_push), BATCH)]

for i, batch in enumerate(batches):
    print(f"\n=== Batch {i+1}/{len(batches)} ({len(batch)} files) ===")
    
    commit = api_call("GET", f"/git/commits/{base_sha}")
    if not commit:
        print("Failed to get commit")
        continue
    tree_sha = commit["tree"]["sha"]
    
    tree_items = []
    for rel, full, size in batch:
        try:
            with open(full, 'r', encoding='utf-8', errors='ignore') as fh:
                content = fh.read()
        except Exception as e:
            print(f"  Skip (read error): {rel} - {e}")
            continue
        
        blob = api_call("POST", "/git/blobs", {"content": content, "encoding": "utf-8"})
        if not blob:
            print(f"  Skip (blob error): {rel}")
            continue
        tree_items.append({
            "path": rel, "mode": "100644", "type": "blob", "sha": blob["sha"]
        })
        print(f"  + {rel} ({size} bytes)")
    
    if not tree_items:
        continue
    
    tree = api_call("POST", "/git/trees", {"base_tree": tree_sha, "tree": tree_items})
    if not tree:
        print("Failed to create tree")
        continue
    
    new_commit = api_call("POST", "/git/commits", {
        "message": f"Sync batch {i+1}/{len(batches)} ({len(tree_items)} files)",
        "parents": [base_sha],
        "tree": tree["sha"]
    })
    if not new_commit:
        print("Failed to create commit")
        continue
    
    updated = api_call("PATCH", f"/git/refs/heads/{BRANCH}", {
        "sha": new_commit["sha"], "force": False
    })
    if updated:
        base_sha = new_commit["sha"]
        print(f"  Commit: {base_sha[:8]}")
    else:
        print("  Failed to update branch")
    
    time.sleep(1)

print(f"\n=== Done! ===")
print(f"Branch: https://github.com/{OWNER}/{REPO}/tree/{BRANCH}")

#!/usr/bin/env python3
"""
sync-caos-pub.py
Aris Hydronics Inc. — CAOS Publications

Syncs the caos-publications HTML files between GitHub Pages and your local machine.
Changes pushed to GitHub automatically update the live GitHub Pages site.

Usage:
  python3 sync-caos-pub.py          # Pull latest from GitHub
  python3 sync-caos-pub.py --push   # Push local changes to GitHub (updates live site)
  python3 sync-caos-pub.py --status # Show current sync status

Requirements:
  - Git installed on your machine (run: git --version to check)
  - GitHub personal access token stored in 1Password
    (or set GITHUB_TOKEN environment variable)

Setup (first time only):
  1. Public GitHub repo 'caos-publications' must exist at github.com/hooltheworld
  2. GitHub Pages must be enabled: repo Settings → Pages → Deploy from branch → main
  3. Create personal access token at github.com/settings/tokens
     - Scope: repo (full control)
  4. Store token in 1Password as 'GitHub Aris Agent System Token' (same token works)
  5. Run: export GITHUB_TOKEN=$(pbpaste)  [after copying token from 1Password]
  6. Run this script once to link your local folder to the repo

Live site URL: https://hooltheworld.github.io/caos-publications/CAOS-at-Aris.html
"""

import subprocess
import sys
import os
from datetime import datetime

# ── CONFIGURATION ────────────────────────────────────────────────────────────

GITHUB_USERNAME = "hooltheworld"
REPO_NAME = "caos-publications"
LOCAL_PATH = os.path.expanduser(
    "~/Documents/Claude Collaboration/caos-publications"
)

REPO_URL = f"https://github.com/{GITHUB_USERNAME}/{REPO_NAME}.git"
LIVE_URL = f"https://{GITHUB_USERNAME}.github.io/{REPO_NAME}/CAOS-at-Aris.html"

# ── HELPERS ──────────────────────────────────────────────────────────────────

def run(cmd, cwd=None, capture=False):
    """Run a shell command. Returns output if capture=True."""
    result = subprocess.run(
        cmd, cwd=cwd, capture_output=capture, text=True
    )
    if result.returncode != 0 and not capture:
        print(f"Error running: {' '.join(cmd)}")
        if result.stderr:
            print(result.stderr)
        sys.exit(1)
    return result

def get_authenticated_url():
    """Build authenticated repo URL using GitHub token from environment."""
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return f"https://{token}@github.com/{GITHUB_USERNAME}/{REPO_NAME}.git"
    return REPO_URL

def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

# ── COMMANDS ─────────────────────────────────────────────────────────────────

def pull():
    """Pull latest files from GitHub to local machine."""
    if not os.path.exists(os.path.join(LOCAL_PATH, ".git")):
        print(f"First time setup — linking local folder to GitHub repository...")
        print(f"Local folder: {LOCAL_PATH}")

        # Initialize git in the existing folder and link to remote
        run(["git", "-C", LOCAL_PATH, "init"])
        run(["git", "-C", LOCAL_PATH, "remote", "add", "origin", get_authenticated_url()])
        run(["git", "-C", LOCAL_PATH, "fetch", "origin"])
        run(["git", "-C", LOCAL_PATH, "checkout", "-b", "main", "--track", "origin/main"])
        print(f"\nDone. Local folder is now linked to GitHub.")
        print(f"Live site: {LIVE_URL}")
    else:
        print(f"Pulling latest changes from GitHub...")
        run(["git", "-C", LOCAL_PATH, "pull", get_authenticated_url(), "main"])
        print(f"\nDone. Files are up to date as of {timestamp()}.")
        print(f"Location: {LOCAL_PATH}")

def push(message=None):
    """Commit and push local changes to GitHub (updates live site within ~60 seconds)."""
    if not os.path.exists(os.path.join(LOCAL_PATH, ".git")):
        print("Local folder is not linked to GitHub yet. Run without --push first.")
        sys.exit(1)

    # Check for changes
    result = run(["git", "-C", LOCAL_PATH, "status", "--porcelain"], capture=True)
    if not result.stdout.strip():
        print("No local changes to push. Live site is already up to date.")
        return

    # Show what changed
    print("Files to be published:")
    print(result.stdout)

    # Commit message
    if not message:
        message = input("Commit message (or press Enter for timestamp): ").strip()
        if not message:
            message = f"Publication update — {timestamp()}"

    # Stage, commit, push
    run(["git", "-C", LOCAL_PATH, "add", "-A"])
    run(["git", "-C", LOCAL_PATH, "commit", "-m", message])
    run(["git", "-C", LOCAL_PATH, "push", get_authenticated_url(), "main"])
    print(f"\nDone. Changes pushed at {timestamp()}.")
    print(f"Live site updates within ~60 seconds:")
    print(f"  {LIVE_URL}")

def status():
    """Show current sync status."""
    if not os.path.exists(os.path.join(LOCAL_PATH, ".git")):
        print("Local folder is not linked to GitHub yet. Run sync to set up.")
        return

    print(f"Repository: {REPO_URL}")
    print(f"Local path: {LOCAL_PATH}")
    print(f"Live site:  {LIVE_URL}")
    print()

    # Last commit
    result = run(
        ["git", "-C", LOCAL_PATH, "log", "-1", "--format=%h %s (%ar)"],
        capture=True
    )
    print(f"Last published: {result.stdout.strip()}")

    # Local changes
    result = run(
        ["git", "-C", LOCAL_PATH, "status", "--porcelain"],
        capture=True
    )
    if result.stdout.strip():
        print(f"\nUnpublished local changes:")
        print(result.stdout)
        print("Run with --push to publish these changes.")
    else:
        print("Local files: clean (matches live site)")

    # File count
    html_files = [f for f in os.listdir(LOCAL_PATH) if f.endswith(".html")]
    print(f"\nHTML files in publication: {len(html_files)}")
    for f in sorted(html_files):
        print(f"  {f}")

# ── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if "--push" in args:
        message = None
        idx = args.index("--push")
        if idx + 1 < len(args) and not args[idx + 1].startswith("--"):
            message = args[idx + 1]
        push(message)
    elif "--status" in args:
        status()
    else:
        pull()

if __name__ == "__main__":
    main()

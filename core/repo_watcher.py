#!/usr/bin/env uv run
import subprocess
import os
import time
from datetime import datetime

def get_git_repos(root_dir):
    """Finds all git repositories under the given root directory."""
    repos = []
    for root, dirs, files in os.walk(root_dir):
        if ".git" in dirs:
            repos.append(root)
            # Don't recurse into subdirectories of a git repo
            dirs.remove(".git")
    return repos

def get_git_status(repo_path):
    try:
        # Check for unpushed commits
        branch_result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_path, capture_output=True, text=True, check=True
        )
        branch = branch_result.stdout.strip()
        
        # Check for unpushed commits (against origin)
        unpushed = subprocess.run(
            ["git", "log", f"origin/{branch}..{branch}"],
            cwd=repo_path, capture_output=True, text=True
        )
        
        # Check for dirty working directory
        status_cmd = subprocess.run(
            ["git", "status", "--short"],
            cwd=repo_path, capture_output=True, text=True, check=True
        )
        is_dirty = len(status_cmd.stdout.strip()) > 0
        
        # Calculate how long it has been dirty
        dirty_duration_str = ""
        seconds_ago = 0
        if is_dirty:
            # Get the mtime of the most recently modified file in the repo (excluding .git)
            last_mod = 0
            for root, dirs, files in os.walk(repo_path):
                if ".git" in dirs:
                    dirs.remove(".git")
                for f in files:
                    try:
                        mtime = os.path.getmtime(os.path.join(root, f))
                        if mtime > last_mod:
                            last_mod = mtime
                    except OSError:
                        continue
            
            if last_mod > 0:
                seconds_ago = int(time.time() - last_mod)
                if seconds_ago < 60:
                    dirty_duration_str = "just now"
                elif seconds_ago < 3600:
                    dirty_duration_str = f"{seconds_ago // 60}m ago"
                elif seconds_ago < 86400:
                    dirty_duration_str = f"{seconds_ago // 3600}h ago"
                else:
                    dirty_duration_str = f"{seconds_ago // 86400}d ago"

        return {
            "name": os.path.basename(repo_path),
            "branch": branch,
            "unpushed": len(unpushed.stdout.strip()) > 0,
            "dirty": is_dirty,
            "dirty_duration": dirty_duration_str,
            "seconds_ago": seconds_ago
        }
    except Exception:
        return None

def check_devx_freshness():
    """Checks if the running container matches the latest DevX source code."""
    version_file = "/usr/local/etc/devx_version"
    origin_file = "/usr/local/etc/devx_origin"
    cache_dir = "/devx/.devx_cache"

    if not os.path.exists(version_file):
        return

    with open(version_file, "r") as f:
        build_hash = f.read().strip()

    if build_hash == "unknown":
        return

    # Check if we have a shadow clone to compare against
    if not os.path.exists(cache_dir) or not os.path.exists(os.path.join(cache_dir, "HEAD")):
        return

    try:
        # 1. Fetch latest from shadow clone
        subprocess.run(["git", "fetch", "origin", "main:main"], cwd=cache_dir, capture_output=True, check=True)
        
        # 2. Get the latest remote hash
        remote_hash = subprocess.run(
            ["git", "rev-parse", "main"], 
            cwd=cache_dir, capture_output=True, text=True, check=True
        ).stdout.strip()

        if build_hash != remote_hash:
            print("\033[1;33m--- DevX Freshness Check ---\033[0m")
            print(f"\033[1;31m[!] Outdated Environment: Container build ({build_hash[:8]}) != Remote ({remote_hash[:8]})\033[0m")
            print("    Please run 'git pull' on host and 'devx up' to refresh.\n")
    except Exception:
        pass

def main():
    check_devx_freshness()
    root_dir = "/devx/repos"
    if not os.path.exists(root_dir):
        return

    repos = get_git_repos(root_dir)
    if not repos:
        return

    print("\n\033[1;33m--- DevX Repo Watcher (Multi-Repo) ---\033[0m")
    
    for repo_path in repos:
        status = get_git_status(repo_path)
        if not status:
            continue
            
        if status["dirty"] or status["unpushed"]:
            # Logic: If dirty for < 5 minutes, keep it subtle. If > 1 hour, make it bright red.
            color = "\033[1;36m" # Default cyan
            if status["dirty"]:
                if status["seconds_ago"] > 3600:
                    color = "\033[1;31m" # Bright Red for old changes
                elif status["seconds_ago"] > 300:
                    color = "\033[1;33m" # Yellow for medium changes
                else:
                    color = "\033[0;36m" # Dim Cyan for very fresh changes

            print(f"{color}{status['name']}\033[0m (\033[0;35m{status['branch']}\033[0m):", end=" ")
            issues = []
            if status["dirty"]:
                issues.append(f"Dirty ({status['dirty_duration']})")
            if status["unpushed"]:
                issues.append("\033[1;31mUnpushed\033[0m")
            print(" | ".join(issues))
    
    print("")

if __name__ == "__main__":
    main()

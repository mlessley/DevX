#!/usr/bin/env uv run
import subprocess
import os

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
    # ... (existing code) ...

def check_devx_freshness():
    """Checks if the running container matches the latest DevX source code."""
    version_file = "/usr/local/etc/devx_version"
    cache_dir = "/devx/.devx_cache"
    # Placeholder for the actual DevX repo URL
    repo_url = "https://github.com/youruser/DevX.git" 

    if not os.path.exists(version_file):
        return

    with open(version_file, "r") as f:
        build_hash = f.read().strip()

    if build_hash == "unknown":
        return

    # Check if we have a shadow clone to compare against
    if not os.path.exists(cache_dir):
        return

    try:
        # 1. Fetch latest from shadow clone
        subprocess.run(["git", "fetch"], cwd=cache_dir, capture_output=True, check=True)
        
        # 2. Get the latest remote hash
        remote_hash = subprocess.run(
            ["git", "rev-parse", "origin/main"], 
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
            print(f"\033[1;36m{status['name']}\033[0m (\033[0;35m{status['branch']}\033[0m):", end=" ")
            issues = []
            if status["dirty"]:
                issues.append("\033[1;31mDirty\033[0m")
            if status["unpushed"]:
                issues.append("\033[1;31mUnpushed\033[0m")
            print(" | ".join(issues))
    
    print("")

if __name__ == "__main__":
    main()

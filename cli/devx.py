import sys
import argparse
import subprocess
import os
from pathlib import Path

def run_command(cmd, cwd=None, capture_output=True, silent=False):
    """Helper to run a command in the WSL environment."""
    try:
        result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=capture_output, text=True)
        return result.stdout.strip() if capture_output else None
    except subprocess.CalledProcessError as e:
        if not silent:
            if capture_output:
                print(f"Error running command {' '.join(cmd)}: {e.stderr}")
            else:
                print(f"Error running command {' '.join(cmd)}")
        raise e

def setup_ssh_keys():
    """Generates SSH keys in WSL if they don't exist and prepares them for injection."""
    ssh_dir = Path.home() / ".ssh"
    key_path = ssh_dir / "id_rsa_devx"
    pub_key_path = ssh_dir / "id_rsa_devx.pub"

    if not ssh_dir.exists():
        ssh_dir.mkdir(mode=0o700)

    if not key_path.exists():
        print(f"Generating new SSH key for DevX at {key_path}...")
        run_command(["ssh-keygen", "-t", "rsa", "-b", "4096", "-f", str(key_path), "-N", ""], capture_output=False)
    
    with open(pub_key_path, "r") as f:
        return f.read().strip()

def inject_ssh_key(pub_key):
    """Injects the public key into the running container for both root and devx users."""
    print("Injecting SSH public key into container...")
    for user in ["root", "devx"]:
        home = "/root" if user == "root" else "/devx"
        run_command(["docker", "exec", "devx-sandbox", "mkdir", "-p", f"{home}/.ssh"])
        cmd = f"echo '{pub_key}' >> {home}/.ssh/authorized_keys && chmod 600 {home}/.ssh/authorized_keys && chown -R {user}:{user} {home}/.ssh"
        run_command(["docker", "exec", "devx-sandbox", "sh", "-c", cmd])

def check_docker():
    """Ensure dockerd is running in WSL."""
    try:
        subprocess.run(["docker", "info"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: Docker is not running in WSL. Please start dockerd.")
        sys.exit(1)

def get_windows_ssh_config_path():
    """Returns the path to the Windows SSH config file from WSL."""
    try:
        # Use cmd.exe to get the USERPROFILE environment variable directly
        win_profile = run_command(["cmd.exe", "/c", "echo %USERPROFILE%"]).strip()
        if not win_profile or "%USERPROFILE%" in win_profile:
            # Fallback if cmd.exe fails or returns literal
            win_user = run_command(["cmd.exe", "/c", "echo %USERNAME%"]).strip()
            config_path = Path(f"/mnt/c/Users/{win_user}/.ssh/config")
        else:
            # Convert Windows path (C:\Users\...) to WSL path (/mnt/c/Users/...)
            wsl_profile = run_command(["wslpath", win_profile]).strip()
            config_path = Path(wsl_profile) / ".ssh" / "config"
        return config_path
    except Exception as e:
        print(f"Debug: Failed to resolve Windows SSH path: {e}")
        return None

def update_windows_ssh_config():
    """Updates the Windows SSH config to include the 'devx' host."""
    config_path = get_windows_ssh_config_path()
    if not config_path:
        print("Warning: Could not locate Windows SSH config path.")
        return

    # If we can't even check existence of the parent, we likely have a mount/permission issue
    try:
        if not config_path.parent.exists():
            print(f"Creating Windows SSH directory: {config_path.parent}")
            config_path.parent.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        print(f"Error: Permission denied accessing {config_path.parent}.")
        print("Please ensure your WSL has permission to write to your Windows user profile.")
        return

    config_entry = """
Host devx
    HostName 127.0.0.1
    Port 2222
    User devx
    IdentityFile ~/.ssh/id_rsa_devx
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
"""
    
    # We need to handle the IdentityFile path carefully. 
    # Since the key is generated in WSL, we should probably copy it to Windows .ssh too.
    wsl_key = Path.home() / ".ssh" / "id_rsa_devx"
    win_key = config_path.parent / "id_rsa_devx"
    
    if wsl_key.exists() and not win_key.exists():
        print(f"Copying DevX key to Windows SSH directory: {win_key}")
        run_command(["cp", str(wsl_key), str(win_key)])

    content = ""
    if config_path.exists():
        with open(config_path, "r") as f:
            content = f.read()

    if "Host devx" in content:
        print("SSH config for 'devx' already exists in Windows.")
    else:
        print(f"Appending 'devx' host to Windows SSH config at {config_path}...")
        with open(config_path, "a") as f:
            f.write(config_entry)

def up(args):
    """Starts the DevX sandbox."""
    check_docker()
    
    # Get the directory of the current script to find core/
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    core_dir = os.path.join(project_root, "core")
    
    # 1. Setup SSH keys locally in WSL
    pub_key = setup_ssh_keys()

    # Get current git hash and origin for build signature
    try:
        current_hash = run_command(["git", "rev-parse", "HEAD"], cwd=project_root, silent=True)
    except Exception:
        current_hash = "unknown"

    try:
        current_origin = run_command(["git", "remote", "get-url", "origin"], cwd=project_root, silent=True)
    except Exception:
        current_origin = "unknown"

    if current_origin != "unknown":
        print(f"Starting DevX Sandbox (Build Signature: {current_hash[:8]}, Origin: {current_origin})...")
    else:
        print(f"Starting DevX Sandbox (Build Signature: {current_hash[:8]})...")
    
    # Use --build-arg to inject the version and origin
    try:
        run_command([
            "docker", "compose", "build", 
            "--build-arg", f"DEVX_VERSION={current_hash}",
            "--build-arg", f"DEVX_ORIGIN={current_origin}"
        ], cwd=core_dir)
        run_command(["docker", "compose", "up", "-d"], cwd=core_dir)
    except Exception:
        run_command([
            "docker-compose", "build", 
            "--build-arg", f"DEVX_VERSION={current_hash}",
            "--build-arg", f"DEVX_ORIGIN={current_origin}"
        ], cwd=core_dir)
        run_command(["docker-compose", "up", "-d"], cwd=core_dir)
    
    # 2. Inject the key into the container
    inject_ssh_key(pub_key)
    
    # 3. Update Windows SSH config
    update_windows_ssh_config()
    
    print("Sandbox is up and running.")

def down(args):
    """Stops the DevX sandbox."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    core_dir = os.path.join(os.path.dirname(script_dir), "core")
    
    print("Stopping DevX Sandbox...")
    try:
        run_command(["docker", "compose", "down"], cwd=core_dir)
    except Exception:
        run_command(["docker-compose", "down"], cwd=core_dir)
    print("Sandbox stopped.")

def status(args):
    """Checks the status of the DevX sandbox."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    core_dir = os.path.join(os.path.dirname(script_dir), "core")
    
    try:
        output = run_command(["docker", "compose", "ps"], cwd=core_dir)
    except Exception:
        output = run_command(["docker-compose", "ps"], cwd=core_dir)
    print(output)

def main():
    parser = argparse.ArgumentParser(description="DevX 2.0 Orchestrator")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Up command
    subparsers.add_parser("up", help="Start the sandbox")
    
    # Down command
    subparsers.add_parser("down", help="Stop the sandbox")
    
    # Status command
    subparsers.add_parser("status", help="Check sandbox status")

    args = parser.parse_args()

    if args.command == "up":
        up(args)
    elif args.command == "down":
        down(args)
    elif args.command == "status":
        status(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

# DevX 2.0: High-Performance Development Sandbox

DevX 2.0 is a high-performance, containerized development environment designed to bridge the gap between your host machine and a native Linux execution layer. It provides a rock-solid, persistent sandbox for engineering workflows where speed, isolation, and consistency are paramount.

## Key Features

- **Universal Bridge**: A cross-platform entry point (`./devx`) that works on Windows (via WSL), macOS, and Linux.
- **Volume-Native Performance**: All project data and user settings live in named Docker volumes (ext4), bypassing slow host-to-container file system overhead for maximum I/O performance.
- **Pure UV Runtimes**: Powered by `uv`, providing lightning-fast Python runtime management (3.11, 3.12) and dependency resolution.
- **Self-Aware Infrastructure**: The sandbox knows its own build state. It automatically detects if the running container is outdated compared to the source code and warns you to refresh.
- **Multi-Repo Monitoring**: An integrated `repo_watcher` provides a concise summary of the Git status for all projects in your sandbox every time you log in.
- **Automated Connectivity**: Automatically configures your host's SSH client to connect to the sandbox with a single command: `ssh devx`.

## Architecture

1. **Host**: Windows 11 (via WSL2), macOS, or Linux.
2. **Controller**: The orchestration layer running `dockerd` and the DevX CLI.
3. **Sandbox (Docker)**: A hardened Debian 13 (Trixie) environment where your code actually runs.

## Getting Started

### Prerequisites
- **Windows**: WSL2 (Ubuntu) and Docker Desktop (or native Docker inside WSL2).
- **macOS/Linux**: Docker and Python 3.

### Installation
1. Clone this repository to your host machine.
2. Open a terminal in the project root.
3. Initialize the sandbox:
   ```bash
   ./devx up
   ```
   *(On Windows CMD/PowerShell, you can still use `devx.bat up`)*

### Usage
- **Start/Update**: `./devx up`
- **Check Status**: `./devx status`
- **Stop**: `./devx down`
- **Connect**: `ssh devx` (or use VS Code Remote-SSH to connect to the `devx` host).

## Project Structure

- `cli/`: The orchestrator logic (Python).
- `core/`: Docker infrastructure, entrypoint scripts, and the `repo_watcher`.
- `devx`: The universal shell bridge.
- `devx.bat`: Windows CMD/PowerShell convenience bridge.
- `/devx/`: The persistent root inside the container (Home directory, repos, and tools).

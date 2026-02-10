# DevX 2.0: High-Performance Development Sandbox

DevX 2.0 is a high-performance, containerized development environment designed to bridge the gap between a Windows host and a native Linux execution layer. It provides a rock-solid, persistent sandbox for engineering workflows where speed, isolation, and consistency are paramount.

## Key Features

- **Windows-to-WSL Bridge**: A zero-dependency entry point (`devx.bat`) that allows you to manage your Linux sandbox directly from the Windows command line.
- **Volume-Native Performance**: All project data and user settings live in named Docker volumes (ext4), bypassing the slow Windows file system (9p) for maximum I/O performance.
- **Pure UV Runtimes**: Powered by `uv`, providing lightning-fast Python runtime management (3.11, 3.12) and dependency resolution.
- **Self-Aware Infrastructure**: The sandbox knows its own build state. It automatically detects if the running container is outdated compared to the source code and warns you to refresh.
- **Multi-Repo Monitoring**: An integrated `repo_watcher` provides a concise summary of the Git status for all projects in your sandbox every time you log in.
- **Automated Connectivity**: Automatically configures your Windows SSH client to connect to the sandbox with a single command: `ssh devx`.

## Architecture

1. **Host (Windows 11)**: Your UI and IDE (VS Code).
2. **Controller (WSL2)**: The orchestration layer running `dockerd` and the DevX CLI.
3. **Sandbox (Docker)**: A hardened Debian 13 (Trixie) environment where your code actually runs.

## Getting Started

### Prerequisites
- Windows 11 with WSL2 (Ubuntu) installed.
- Docker Desktop (or native Docker inside WSL2).

### Installation
1. Clone this repository into your Windows machine.
2. Open a terminal in the project root.
3. Initialize the sandbox:
   ```powershell
   .\devx.bat up
   ```

### Usage
- **Start/Update**: `.\devx.bat up`
- **Check Status**: `.\devx.bat status`
- **Stop**: `.\devx.bat down`
- **Connect**: `ssh devx` (or use VS Code Remote-SSH to connect to the `devx` host).

## Project Structure

- `cli/`: The orchestrator logic (Python).
- `core/`: Docker infrastructure, entrypoint scripts, and the `repo_watcher`.
- `devx.bat`: The Windows entry point.
- `/devx/`: The persistent root inside the container (Home directory, repos, and tools).

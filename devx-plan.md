# DevX 2.0: High-Performance AI Sandbox & Orchestrator

## 1. Architectural Vision
DevX 2.0 is a three-tier development environment designed for high-performance AI Engineering and Agentic workflows.

- **Tier 1 (Host):** Windows 11. Provides the UI (VS Code) and the entry point (`devx.bat`).
- **Tier 2 (Controller):** WSL2 (Ubuntu) running native `dockerd`. Handles Python orchestration via `cli/devx.py`.
- **Tier 3 (Sandbox):** Isolated Docker Containers running Debian 13 (Trixie). This is where the code lives and where AI agents execute.

## 2. Technical Constraints (Crucial)
- **Zero Host Dependencies:** No Python or Bash required on Windows. The `.bat` file bridges to the WSL Python interpreter.
- **Volume-Native Storage:** **NO BIND MOUNTS** from C:\ for project code. All workspace data lives in named Docker Volumes (ext4) for maximum I/O speed.
- **High-Performance Runtimes:** Uses `uv` for lightning-fast Python management.
- **Connectivity:** SSH-based access with automated Windows `~/.ssh/config` management.
- **Security:** Multi-stage Docker builds. Key-based authentication with password fallback enabled for recovery.

## 3. Implementation Summary

### Phase 1: The Bridge (Windows -> WSL)
- [x] 1.1 **`devx.bat`**: A robust Windows batch script that translates its own location to a WSL path using `wsl wslpath` and invokes the WSL Python interpreter.
- [x] 1.2 **`cli/devx.py`**: The orchestrator core using `argparse`. Commands: `up`, `down`, `status`.
- [x] 1.3 **Path Verification**: Confirmed argument passing from Windows CMD to WSL Python.

### Phase 2: Docker Orchestration (UV & Trixie)
- [x] 2.1 **`core/Dockerfile`**: High-performance multi-stage build.
    - Uses `ghcr.io/astral-sh/uv` to manage Python 3.11 and 3.12 runtimes.
    - Base OS: `debian:trixie-slim` (Debian 13).
    - Includes `sshd`, `git`, `curl`, and a dedicated `devx` user.
- [x] 2.2 **`core/docker-compose.yml`**:
    - Defines the `devx_workspace` named volume mapped to `/devx`.
    - Exposes SSH on `127.0.0.1:2222`.
- [x] 2.3 **`devx.py up` logic**: Automated `dockerd` check and `docker compose up -d --build` orchestration.

### Phase 3: Connectivity & DX
- [x] 3.1 **SSH Key Management**: Automatic generation of `id_rsa_devx` in WSL and injection into the container's `authorized_keys` for both `root` and `devx` users.
- [x] 3.2 **SSH Config Automation**: Automated discovery of Windows `%USERPROFILE%` and injection of the `Host devx` entry into the Windows SSH config.
- [x] 3.3 **`repo_watcher.py`**: A `uv run` script installed in `/usr/local/bin` that monitors multiple repositories under `/devx/repos` for dirty states and unpushed commits.

### Phase 4: Self-Maintenance & Integrity
- [x] 4.1 **Build Signatures**: Injects the local Git commit hash (`DEVX_VERSION`) and remote origin (`DEVX_ORIGIN`) into the image during build.
- [x] 4.2 **Entrypoint Initialization**: `core/entrypoint.sh` handles volume-native home directory setup, copying skeleton files (`.bashrc`), and fixing permissions.
- [x] 4.3 **Freshness Check**: `repo_watcher.py` maintains a shadow clone in `/devx/.devx_cache` and warns the user if the running container is outdated compared to the GitHub source.

# DevX 2.0: High-Performance AI Sandbox & Orchestrator

## 1. Architectural Vision
DevX 2.0 is a three-tier development environment designed for high-performance AI Engineering and Agentic workflows.

- **Tier 1 (Host):** Windows 11. Provides the UI (VS Code) and the entry point (`devx.bat`).
- **Tier 2 (Controller):** WSL2 (Ubuntu) running native `dockerd`. This layer handles all Python orchestration logic via `cli/devx.py`.
- **Tier 3 (Sandbox):** Isolated Docker Containers. This is where the code lives and where AI agents execute.

## 2. Technical Constraints (Crucial)
- **Zero Host Dependencies:** No Python or Bash required on Windows. The `.bat` file must bridge to the WSL Python interpreter.
- **Volume-Native Storage:** **NO BIND MOUNTS** from C:\ for project code. All workspace data MUST live in named Docker Volumes (ext4) for maximum I/O speed.
- **Connectivity:** Uses SSHD + ProxyJump. VS Code connects to the container via `localhost` forwarding, making the container appear as a remote Linux VM.
- **Security:** Multi-stage Docker builds. Prod-ready base image with a hardened DevX layer (SSH Key-auth only, no passwords).

## 3. Implementation Task List

### Phase 1: The Bridge (Windows -> WSL)
- [ ] 1.1 Create `devx.bat`: A Windows batch script that translates its own location to a WSL path and calls the Linux Python interpreter.
- [ ] 1.2 Create `cli/devx.py`: The orchestrator skeleton using `argparse`. Commands: `up`, `down`, `status`, `logs`.
- [ ] 1.3 Verify pathing: Ensure `devx.bat` can pass arguments to `devx.py` successfully.

### Phase 2: Docker Orchestration (Volume-Native)
- [ ] 2.1 Create `core/Dockerfile`: Multi-stage build.
    - Stage 1: `python:3.11-slim` (The "Prod" base).
    - Stage 2: Add `sshd`, `git`, `curl`, and SSH keys for the "DevX" layer.
- [ ] 2.2 Create `core/docker-compose.yml`:
    - Define a **Named Volume** (e.g., `devx_workspace`).
    - Map the volume to `/work` in the container.
    - Expose the SSH port ONLY to `127.0.0.1`.
- [ ] 2.3 Implement `devx.py up` logic: Must check if `dockerd` is running in WSL and trigger `docker-compose up -d`.

### Phase 3: Connectivity & DX
- [ ] 3.1 SSH Key Management: `devx.py` should generate local SSH keys if they don't exist and inject the public key into the container.
- [ ] 3.2 SSH Config Automation: Update `~/.ssh/config` on the Windows host to include a `Host devx` entry with the correct ProxyJump/Port settings.
- [ ] 3.3 The "Ghost Watcher": Create a lightweight Python script for the container's `.bashrc` that monitors Git status in `/devx/repos` and warns of unpushed code.

### Phase 4: Self-Maintenance
- [ ] 4.1 "Freshness" Check: Implement a `git fetch` in `devx.py` to compare the local signature against a shadow clone/remote and warn the user to restart if updates exist.
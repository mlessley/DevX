# DevX 2.0: Roadmap to Agentic Autonomy

With the core sandbox and orchestration bridge complete, we are moving from **Infrastructure** to **Intelligence**. This plan focuses on making the sandbox a first-class environment for AI agents.

## Phase 5: The Agentic Foundation
- [ ] **5.1 MCP Integration**: Research and implement a Model Context Protocol (MCP) server inside the container to expose sandbox tools (Git, UV, File System) to LLMs.
- [ ] **5.2 Secure Tool Execution**: Create a `/devx/bin/exec-agent` wrapper that logs all agent-initiated commands to `/var/log/devx_adhoc_history` for auditability.
- [ ] **5.3 Workspace Context**: Create a `devx ctx` command that generates a "Context Snapshot" (current repos, active python version, disk usage) to be fed into an LLM's system prompt.

## Phase 6: Advanced DX & Connectivity
- [ ] **6.1 VS Code "One-Click"**: Implement `devx open <repo>` which ensures the container is up and triggers `code --remote ssh-remote+devx /devx/repos/<repo>` on the Windows host.
- [ ] **6.2 Port Forwarding Manager**: Add a `devx forward <port>` command to dynamically manage SSH port tunnels for web servers running inside the sandbox.
- [ ] **6.3 Tailscale/ZeroTier Integration**: (Optional) Research adding a mesh VPN layer so the sandbox can be reached securely from outside the local machine.

## Phase 7: Automated Maintenance (The "Self-Healing" Sandbox)
- [ ] **7.1 Auto-Cleanup**: Implement `devx prune` to safely remove unused Docker layers and old `uv` cache files without touching `/devx/repos`.
- [ ] **7.2 Health Check**: Add a `devx doctor` command to verify WSL status, Docker daemon health, and SSH connectivity.
- [ ] **7.3 Dependency Watcher**: Extend `repo_watcher.py` to notify the user if a `pyproject.toml` has changed and a `uv sync` is required.

## Phase 8: Agentic "Ghost" Mode
- [ ] **8.1 Background Agents**: Implement a way to run long-lived "Ghost Agents" in the background that can perform tasks like automated testing or documentation generation while the user is away.
- [ ] **8.2 Event Bus**: Create a simple file-based event bus in `/devx/.events` so the host and container can signal each other (e.g., "Build Finished" notification on Windows).

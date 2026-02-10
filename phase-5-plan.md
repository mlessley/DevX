# Phase 5: Agentic Foundation - Implementation Plan

This phase transforms the DevX 2.0 sandbox into a machine-readable environment, allowing AI agents to operate with high-performance tools and full situational awareness.

## 5.1 Workspace Context (`devx ctx`)
**Goal**: Provide a "Single Source of Truth" for the sandbox state that can be fed to LLMs.
- [ ] Create `core/context_manager.py`: A script to aggregate sandbox metadata.
    - List all repos in `/devx/repos` with their current branch and "dirty" status.
    - Identify the active Python version and installed `uv` tools.
    - Summarize recent ad-hoc changes from `/var/log/devx_adhoc_history`.
- [ ] Add `ctx` command to `cli/devx.py`:
    - `devx ctx`: Output a beautiful Markdown summary for humans.
    - `devx ctx --json`: Output raw data for AI agents.

## 5.2 Secure Agent Wrapper (`devx-exec`)
**Goal**: Audit and control agent actions.
- [ ] Create `/devx/bin/devx-exec`: A bash wrapper for agent commands.
    - Automatically logs command, timestamp, and exit code to `devx_adhoc_history`.
    - Enforces execution within the `/devx` volume.
- [ ] Update `Dockerfile`: Ensure `devx-exec` is in the PATH and executable.

## 5.3 Model Context Protocol (MCP) Integration
**Goal**: Enable direct tool-use for LLMs (Claude Desktop, Cursor, etc.).
- [ ] Research/Select MCP Server implementation:
    - Option A: Use a standard `filesystem` MCP server pointed at `/devx`.
    - Option B: Create a custom `devx-mcp` server that exposes `uv` and `git` as native tools.
- [ ] Configure `devx.py` to manage the MCP lifecycle:
    - `devx mcp start/stop`: Manage the MCP server process inside the container.
- [ ] Connectivity: Ensure the host (Windows) can talk to the containerized MCP server via the SSH bridge.

## 5.4 Agentic "Welcome Mat"
**Goal**: Orient agents immediately upon connection.
- [ ] Update `entrypoint.sh`:
    - If the user is an agent (detected via SSH_CLIENT or environment), auto-run `devx ctx` to provide immediate context.
    - Display a "Tool Inventory" (UV, Git, DevX-Exec) on login.

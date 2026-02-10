#!/bin/bash
# --- DevX Entrypoint Script ---

# Ensure the repos directory exists on the volume
mkdir -p /devx/repos

# Initialize shadow clone for freshness check if it doesn't exist
if [ ! -d /devx/.devx_cache ]; then
    echo "Initializing DevX shadow clone..."
    # We clone the repo into a hidden directory on the volume
    # Note: This requires git to be able to reach the repo
    # For now, we'll just create the directory as a placeholder
    mkdir -p /devx/.devx_cache
    # git clone --bare https://github.com/youruser/DevX.git /devx/.devx_cache
fi

# Copy skeleton files if they don't exist (since /devx is a volume)
if [ ! -f /devx/.bashrc ]; then
    echo "Initializing /devx with default dotfiles..."
    cp /etc/skel/.bashrc /devx/.bashrc
    cp /etc/skel/.profile /devx/.profile
    cp /etc/skel/.bash_logout /devx/.bash_logout
fi

# Re-apply the Repo Watcher to .bashrc on the volume if it's missing
# Using the pure 'uv run' way
if ! grep -q "repo_watcher.py" /devx/.bashrc; then
    echo "uv run /usr/local/bin/repo_watcher.py" >> /devx/.bashrc
fi

# Add version switching aliases for convenience
if ! grep -q "alias use-py" /devx/.bashrc; then
    echo "alias use-py311='uv python pin 3.11'" >> /devx/.bashrc
    echo "alias use-py312='uv python pin 3.12'" >> /devx/.bashrc
fi

# Fix permissions for the devx user for the entire home directory
chown -R devx:devx /devx

# Execute the original command (sshd)
exec "$@"

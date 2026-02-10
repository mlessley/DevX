#!/bin/bash
# --- DevX Entrypoint Script ---

# Ensure the repos directory exists on the volume
mkdir -p /devx/repos

# Initialize shadow clone for freshness check if it doesn't exist
if [ ! -d /devx/.devx_cache ]; then
    echo "Initializing DevX shadow clone..."
    DEVX_ORIGIN=$(cat /usr/local/etc/devx_origin)
    if [ "$DEVX_ORIGIN" != "unknown" ]; then
        # We clone the repo into a hidden directory on the volume
        git clone --bare "$DEVX_ORIGIN" /devx/.devx_cache
    else
        mkdir -p /devx/.devx_cache
    fi
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

# Add version switching aliases and a better prompt
if ! grep -q "alias use-py" /devx/.bashrc; then
    echo "alias use-py311='uv python pin 3.11'" >> /devx/.bashrc
    echo "alias use-py312='uv python pin 3.12'" >> /devx/.bashrc
fi

# Inject a high-performance, informative prompt
if ! grep -q "DevX 2.0 Prompt Configuration" /devx/.bashrc; then
    cat << 'EOF' >> /devx/.bashrc

# DevX 2.0 Prompt Configuration
# [Time] devx@devx [Dir] (git:branch)
parse_git_branch() {
     git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/ (\1)/'
}
export PS1="\[\033[01;30m\][\t] \[\033[01;32m\]devx@devx \[\033[01;34m\]\w\[\033[01;35m\]\$(parse_git_branch)\[\033[00m\] \$ "
EOF
fi

# Fix permissions for the devx user for the entire home directory
chown -R devx:devx /devx

# Configure git default branch for the devx user
sudo -u devx git config --global init.defaultBranch main

# Execute the original command (sshd)
exec "$@"

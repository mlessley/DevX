# --- Stage 1: Binary Source (uv) ---
FROM ghcr.io/astral-sh/uv:latest AS uv_bin

# --- Stage 2: Final (DevX Environment) ---
FROM debian:trixie-slim AS devx

# 1. Install uv binaries
COPY --from=uv_bin /uv /uvx /usr/bin/

# 2. Set uv environment variables
ENV UV_PYTHON_INSTALL_DIR=/opt/python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Install System Dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server \
    git \
    curl \
    sudo \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 4. Install Python Runtimes via uv
RUN uv python install 3.11 3.12

# 5. Configure SSH (Key-auth + Password fallback)
RUN mkdir -p /var/run/sshd \
    && sed -i 's/^#*PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config

# 6. Create devx user with home at /devx
RUN useradd -d /devx -s /bin/bash devx \
    && echo "root:devx" | chpasswd \
    && echo "devx:devx" | chpasswd \
    && usermod -aG sudo devx \
    && echo "devx ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# 7. Install Orchestration Tools
ARG DEVX_VERSION=unknown
RUN echo $DEVX_VERSION > /usr/local/etc/devx_version

RUN touch /var/log/devx_adhoc_history && chmod 666 /var/log/devx_adhoc_history
COPY repo_watcher.py /usr/local/bin/repo_watcher.py
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/repo_watcher.py /usr/local/bin/entrypoint.sh

# 8. Setup root's environment (devx is handled by entrypoint)
RUN echo "uv run /usr/local/bin/repo_watcher.py" >> /root/.bashrc

RUN mkdir -p /devx
EXPOSE 22

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["/usr/sbin/sshd", "-D"]

# Use Python 3.13.2-slim base image (consistent with hacs_smartcocoon)
FROM python:3.13.2-slim

# Install essential development tools
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    make \
    jq \
    wget \
    unzip \
    zip \
    libatomic1 \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI (required for act)
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update \
    && apt-get install -y docker-ce-cli \
    && rm -rf /var/lib/apt/lists/*

# Install GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update \
    && apt-get install -y gh \
    && rm -rf /var/lib/apt/lists/*

# Install act (GitHub Actions local runner)
RUN curl https://raw.githubusercontent.com/nektos/act/master/install.sh | bash

# Install additional Python development tools
RUN python3 -m pip install --upgrade pip

ARG PYPROJECT_FILE='pyproject.toml'
COPY ${PYPROJECT_FILE} .

ARG REQUIREMENTS_FILE='requirements_test.txt'
COPY requirements.txt .
COPY ${REQUIREMENTS_FILE} .
RUN python3 -m pip install -r ${REQUIREMENTS_FILE}

# Install additional tools for GitHub Actions compatibility
RUN python3 -m pip install mypy pytest-cov

# Install additional useful development tools
RUN apt-get update && apt-get install -y \
    vim \
    nano \
    tree \
    htop \
    less \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Create vscode user (required for devcontainer)
RUN groupadd --gid 1000 vscode \
    && useradd --uid 1000 --gid vscode --shell /bin/bash --create-home vscode \
    && usermod -aG sudo vscode \
    && echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Switch to vscode user
USER vscode
WORKDIR /workspaces/pysmartcocoon

ENTRYPOINT []

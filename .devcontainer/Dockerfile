# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.245.2/containers/python-3/.devcontainer/base.Dockerfile

# [Choice] Python version (use -bullseye variants on local arm64/Apple Silicon): 3, 3.10, 3.9, 3.8, 3.7, 3.6, 3-bullseye, 3.10-bullseye, 3.9-bullseye, 3.8-bullseye, 3.7-bullseye, 3.6-bullseye, 3-buster, 3.10-buster, 3.9-buster, 3.8-buster, 3.7-buster, 3.6-buster
ARG VARIANT="3.12"
FROM mcr.microsoft.com/vscode/devcontainers/python:1-${VARIANT}

ARG PYPROJECT_FILE='pyproject.toml'
COPY ${PYPROJECT_FILE} .

ARG REQUIREMENTS_FILE='requirements_test.txt'
COPY requirements.txt .
COPY ${REQUIREMENTS_FILE} .
RUN python3 -m pip install -r ${REQUIREMENTS_FILE}

ENTRYPOINT []

# syntax=docker/dockerfile:1.9

# --- Build Stage ---
# Use Ubuntu Noble for a consistent build environment with necessary tools
FROM ubuntu:noble AS build

# Use shell with exit on error and command echoing (good practice)
SHELL ["sh", "-exc"]

# Ensure apt-get doesn't prompt for input
ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies: build tools and Python dev headers (for C extensions)
RUN apt-get update -qy && \
    apt-get install -qyy \
        -o APT::Install-Recommends=false \
        -o APT::Install-Suggests=false \
        build-essential \
        ca-certificates \
        python3.12-dev \
        git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install uv securely
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Configure uv for optimal container builds
# - Copy links to avoid hardlink issues in some environments.
# - Compile bytecode for faster Lambda cold starts.
# - Prevent accidental downloads of Python distributions.
# - Specify the exact Python interpreter to use.
# - Set the target directory to /var/task, where Lambda expects code/deps.
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=/usr/bin/python3.12 \
    UV_PROJECT_ENVIRONMENT=/var/task

# Create the target directory explicitly (good practice without implicit creation by uv sync)
RUN mkdir -p /var/task

# Copy project definition files first for dependency caching layer
COPY pyproject.toml uv.lock ./

# Install DEPENDENCIES only. This layer is cached until uv.lock or pyproject.toml change.
# uv sync will use the copied files in the current directory.
# Note: Without --mount=type=cache, uv's internal cache is less effective across builds.
RUN uv sync \
        --locked \
        --no-dev \
        --no-install-project

# Install the APPLICATION code itself into the /var/task environment.
# Dependencies are already present from the previous step.
COPY . /src
WORKDIR /src
RUN uv sync \
        --locked \
        --no-dev \
        --no-editable # Installs the package defined in pyproject.toml


##########################################################################

# --- Final Runtime Stage ---
# Use the official AWS Lambda Python base image
FROM public.ecr.aws/lambda/python:3.12

SHELL ["sh", "-exc"]

# Install user management tools, create user/group, then clean up
RUN microdnf install -y shadow-utils && \
    # Now create the group and user USING FULL PATHS
    /usr/sbin/groupadd -r app --gid 1000 && \
    /usr/sbin/useradd -r -d /var/task -g app --uid 1000 --shell /sbin/nologin -c "Application User" app && \
    # Clean up package manager cache to keep image small
    microdnf clean all && \
    rm -rf /var/cache/dnf

# Install any *additional* OS-level runtime dependencies needed by your code
# that are NOT already included in the base Lambda image. Most apps won't need this.
# Example: RUN microdnf install -y some-package && microdnf clean all && rm -rf /var/cache/dnf

# Copy the application code and all installed dependencies from the build stage
# into the location Lambda expects (/var/task).
# Change ownership to the non-root user.
COPY --from=build --chown=app:app /var/task /var/task

ENV PYTHONPATH="${PYTHONPATH}:/var/task/lib/python3.12/site-packages"
# Set the working directory
WORKDIR /var/task

# Switch to the non-root user
# USER app

# Default command (override by Lambda's ImageConfig in template.yaml)
# Ensure this path matches your actual handler location (e.g., src.app...)
CMD ["app.handlers.api_handler.handler"]

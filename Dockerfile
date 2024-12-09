ARG PYTHON_VERSION=3.10.12
FROM python:${PYTHON_VERSION}-slim as base

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /imagesearcher

# Ensure the directory is writable by appuser
RUN chown -R root:root /imagesearcher

# Create a non-root user for security purposes
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/imagesearcher" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Install system dependencies (git) and clean up to reduce image size
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies with pip cache enabled
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Change ownership of the project directory to the appuser
RUN chown -R appuser:appuser /imagesearcher

# Create the .cache directory and make sure it's writable
RUN mkdir -p /imagesearcher/.cache && chown -R appuser:appuser /imagesearcher/.cache

# Switch to the non-root user
USER appuser

COPY . .

EXPOSE 5000

CMD gunicorn 'app:app' --bind=0.0.0.0:5000 --timeout 120 --workers 20 --worker-class gevent


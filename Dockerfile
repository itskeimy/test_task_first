FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8099 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency definition files first for efficient Docker layer caching
COPY pyproject.toml uv.lock ./

# Install project dependencies
RUN uv sync --frozen --no-install-project --no-dev

# Copy application source code
COPY . /app

# Install project itself
RUN uv sync --frozen --no-dev && chmod +x /app/entrypoint.sh

EXPOSE 8099

ENTRYPOINT ["/app/entrypoint.sh"]

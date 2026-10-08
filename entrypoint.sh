#!/bin/sh
set -e

# Apply database migrations
uv run python manage.py migrate --no-input

# Start gunicorn on port 8099 with 1 worker and 4 threads
exec uv run gunicorn config.wsgi:application \
  --bind 0.0.0.0:8099 \
  --workers 1 \
  --threads 4 \
  --access-logfile - \
  --error-logfile -

#!/bin/sh
set -e

# Collect static files into STATIC_ROOT for Nginx to serve directly
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate --no-input

# Start gunicorn on port 8099 with 1 worker and 4 threads
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8099 \
  --workers 1 \
  --threads 4 \
  --access-logfile - \
  --error-logfile -

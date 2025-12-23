#!/usr/bin/env bash

# Start Celery worker and Gunicorn in the same container so both share the
# local filesystem (needed for processing uploaded CSVs on the free Render tier).
set -euo pipefail

python manage.py migrate

# Start Celery worker in the background. Limit concurrency to keep resource usage low.
celery -A config worker --loglevel=info --concurrency=2 &

# Start the Django app via Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:"${PORT:-8000}"


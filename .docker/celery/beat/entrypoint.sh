#!/bin/bash
set -e

# Activate venv
source /home/appuser/app/venv/bin/activate

# Run migrations
echo "Running migrations..."
python manage.py migrate django_celery_beat

celery -A skeleton beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
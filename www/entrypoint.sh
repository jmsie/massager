#!/bin/sh

# Make migrations
python manage.py makemigrations

# Apply database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start server
exec "$@"

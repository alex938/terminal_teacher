#!/bin/bash
set -e

echo "🚀 Starting Terminal Teacher..."

# Ensure data directory exists
mkdir -p /app/data

# Run migrations
echo "📦 Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create initial session if needed
echo "🎓 Initializing default session..."
python manage.py shell << PYTHON
from commands.models import TeachingSession
if not TeachingSession.objects.exists():
    TeachingSession.get_active_session()
    print("Created default session")
else:
    print("Session already exists")
PYTHON

echo "✅ Starting Gunicorn server on port 7777..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:7777 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info

#!/bin/bash

set -e

echo "Starting ProjectA..."

if [ -n "$DATABASE_HOST" ]; then
    echo " Waiting for PostgreSQL..."
    while ! nc -z $DATABASE_HOST ${DATABASE_PORT:-5432}; do
        sleep 1
    done
    echo "PostgreSQL is ready!"
fi

if [ -n "$REDIS_HOST" ]; then
    echo "Waiting for Redis..."
    while ! nc -z $REDIS_HOST ${REDIS_PORT:-6379}; do
        sleep 1
    done
    echo "Redis is ready!"
fi

echo "Running migrations..."
python manage.py migrate --noinput

if [ "$DEBUG" != "True" ]; then
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
else
    echo "Skipping collectstatic in DEBUG mode"
fi

if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating superuser..."
    python manage.py shell << EOF
from users.models import CustomUser
if not CustomUser.objects.filter(email='$DJANGO_SUPERUSER_EMAIL').exists():
    CustomUser.objects.create_superuser(
        email='$DJANGO_SUPERUSER_EMAIL',
        first_name='${DJANGO_SUPERUSER_FIRST_NAME:-Admin}',
        last_name='${DJANGO_SUPERUSER_LAST_NAME:-User}',
        password='$DJANGO_SUPERUSER_PASSWORD'
    )
    print('Superuser created!')
else:
    print('Superuser already exists')
EOF
fi

echo "ProjectA is ready!"
exec "$@"
#!/bin/sh
set -e

# База уже готова: compose запускает web только после healthcheck контейнера db
if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
    echo "Running database migrations..."
    python manage.py migrate --noinput
fi

exec "$@"

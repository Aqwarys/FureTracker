#!/bin/sh

# Выходим сразу, если какая-либо команда завершится с ошибкой.
set -e

# Ожидаем, пока база данных станет доступной.
until nc -z db 5432; do
  echo "Waiting for the database..."
  sleep 2
done

# Применяем миграции к базе данных.
echo "Running database migrations..."
python manage.py migrate --noinput

# Сбор статических файлов.
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Запускаем основную команду (Gunicorn), которая была передана в CMD.
exec "$@"

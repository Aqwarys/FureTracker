#!/bin/sh

# Этот скрипт будет запускаться при старте контейнера.

# Выходим сразу, если какая-либо команда завершится с ошибкой.
set -e

# Ожидаем, пока база данных станет доступной.
# healthcheck в docker-compose.yml уже проверяет это,
# но этот дополнительный шаг делает процесс еще более надежным.
until nc -z db 5432; do
  echo "Waiting for the database..."
  sleep 2
done

# Применяем миграции к базе данных.
echo "Running database migrations..."
python manage.py migrate --noinput

# Сбор статических файлов.
# Это также важно для продакшена.
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Запускаем основную команду, переданную в CMD.
# В нашем случае это будет gunicorn.
exec "$@"

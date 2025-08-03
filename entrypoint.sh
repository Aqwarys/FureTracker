set -e

until nc -z db 5432; do
  echo "Waiting for the database..."
  sleep 2
done

echo "Running database migrations..."
python manage.py migrate --noinput
``
echo "Collecting static files..."
python manage.py collectstatic --noinput

exec "$@"

#!/bin/sh
# Первичный выпуск SSL-сертификата. Запускать на сервере один раз, ДО первого `docker compose up -d`
# (nginx не стартует без сертификата). Дальше certbot-контейнер продлевает его сам.
set -eu

cd "$(dirname "$0")/.."
DOMAIN=$(grep -E '^DOMAIN=' .env | cut -d= -f2-)
CERTBOT_EMAIL=$(grep -E '^CERTBOT_EMAIL=' .env | cut -d= -f2-)

docker compose run --rm -p 80:80 --entrypoint certbot certbot certonly --standalone \
    -d "$DOMAIN" -d "www.$DOMAIN" \
    --email "$CERTBOT_EMAIL" --agree-tos --no-eff-email

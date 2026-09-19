# FureTracker

Сайт мебельной компании: клиенты следят за своим заказом по личной ссылке, посетители смотрят портфолио.

## Как устроен доступ к заказам

| Кто | Где | Что видит |
|---|---|---|
| Клиент | `/orders/track/<токен>/` — личная ссылка из админки (поле «Личная ссылка клиента») | Свой заказ, фото/видео, может писать комментарии. Регистрация не нужна |
| Любой посетитель | `/orders/` и `/orders/<номер>/` | Только заказы с галочкой «Показывать в портфолио», без комментариев |
| Сотрудник (`is_staff`) | Везде | Все заказы + форма загрузки фото/видео |

Номера новых заказов случайные (`ORD-7K3QXM`), без похожих символов 0/O, 1/I/L.

## Настройка

Все параметры — в `.env` (шаблон с пояснениями: `.env.example`):

```sh
cp .env.example .env
```

`COMPOSE_FILE` в `.env` определяет режим, после этого везде работает просто `docker compose ...`:

- **dev** — `docker-compose.yml:docker-compose.dev.yml`: runserver с автоперезагрузкой на http://localhost:8000, база доступна на `localhost:5432`.
- **prod** — `docker-compose.yml:docker-compose.prod.yml`: gunicorn + nginx + HTTPS + бэкапы.

## Локальная разработка

```sh
docker compose up -d
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py test
docker compose logs -f web
```

## Продакшен (первый запуск на сервере)

1. Направить A-записи `DOMAIN` и `www.DOMAIN` на IP сервера.
2. Заполнить `.env`: `COMPOSE_FILE=...prod.yml`, `DJANGO_DEBUG=False`, `DJANGO_ALLOWED_HOSTS`, `SITE_URL=https://<домен>`, `DOMAIN`, `CERTBOT_EMAIL`, ключи S3.
3. Выпустить сертификат (один раз, до запуска nginx):
   ```sh
   sh docker/init-ssl.sh
   ```
4. Запустить:
   ```sh
   docker compose up -d --build
   docker compose exec web python manage.py createsuperuser
   ```

Сертификат продлевается автоматически (контейнер `certbot`), nginx подхватывает его сам.

Обновление после `git pull`:

```sh
docker compose up -d --build
```

## Бэкапы базы

Контейнер `db-backup` по расписанию `BACKUP_CRON` (по умолчанию 1-го числа каждого месяца) кладёт дамп в `./backups/` и оставляет `BACKUP_KEEP` последних.

Сделать дамп вручную:

```sh
docker compose exec db-backup sh /scripts/backup.sh
```

Восстановить:

```sh
gunzip -c backups/<файл>.sql.gz | docker compose exec -T db psql -U <POSTGRES_USER> -d <POSTGRES_DB>
```

> Бэкапы лежат на том же сервере. Периодически копируйте `backups/` в другое место (например, в S3-бакет или к себе на компьютер) — иначе при потере сервера они пропадут вместе с базой.

## Файлы

- Фото/видео заказов — в S3-совместимом хранилище, загружаются из браузера напрямую по подписанной ссылке. Можно использовать AWS S3, Cloudflare R2, PS.kz и т.п. — см. `AWS_S3_ENDPOINT_URL` в `.env.example`.
- Статика (css/js/картинки сайта) — отдаётся самим приложением через WhiteNoise, собирается при сборке образа.

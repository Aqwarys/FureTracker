FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Зависимости ставим отдельным слоем — при изменении кода они не переустанавливаются
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Статика собирается при сборке образа (отдаёт WhiteNoise). Настоящие ключи для этого не нужны.
RUN SECRET_KEY=build-only DATABASE_URL=sqlite:////tmp/build.sqlite3 \
    python manage.py collectstatic --noinput -v0

RUN useradd --create-home --uid 1000 app
USER app

EXPOSE 8000

ENTRYPOINT ["sh", "/app/entrypoint.sh"]
# Количество воркеров и таймауты задаются через GUNICORN_CMD_ARGS в .env
CMD ["gunicorn", "furetracker.wsgi:application", "--bind", "0.0.0.0:8000"]

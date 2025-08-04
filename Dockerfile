FROM python:3.12.4-slim-bookworm

WORKDIR /app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install -r requirements.txt


# RUN printf '#!/bin/sh\n\n' > /app/entrypoint.sh \
#     && printf 'set -e\n\n' >> /app/entrypoint.sh \
#     && printf 'until nc -z db 5432; do\n' >> /app/entrypoint.sh \
#     && printf '  echo "Waiting for the database..."\n' >> /app/entrypoint.sh \
#     && printf '  sleep 2\n' >> /app/entrypoint.sh \
#     && printf 'done\n\n' >> /app/entrypoint.sh \
#     && printf 'echo "Running database migrations..."\n' >> /app/entrypoint.sh \
#     && printf 'python manage.py migrate --noinput\n\n' >> /app/entrypoint.sh \
#     && printf 'echo "Collecting static files..."\n' >> /app/entrypoint.sh \
#     && printf 'python manage.py collectstatic --noinput\n\n' >> /app/entrypoint.sh \
#     && printf 'exec "$@"\n' >> /app/entrypoint.sh \
#     && chmod +x /app/entrypoint.sh

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

COPY . /app/

RUN mkdir -p /var/log/django/

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "furetracker.wsgi:application"]
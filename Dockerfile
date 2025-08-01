FROM python:3.12.4-slim-bookworm

WORKDIR /app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    netcat-traditional \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app/

RUN dos2unix /app/entrypoint.sh && chmod +x /app/entrypoint.sh

RUN mkdir -p /var/log/django/

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "furetracker.wsgi:application"]

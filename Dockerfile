FROM python:3.12.4-slim-bookworm

WORKDIR /app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install -r requirements.txt


COPY . /app/

RUN mkdir -p /var/log/django/


EXPOSE 8000


CMD ["gunicorn", "--bind", "0.0.0.0:8000", "furetracker.wsgi:application"]

# Dockerfile
FROM python:3.11-alpine
WORKDIR /app
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /app/

RUN apk add --no-cache postgresql-dev gcc python3-dev musl-dev \
    && mkdir -p /var/log/django/


RUN pip install --no-cache-dir -r requirements.txt && \
    apk del gcc python3-dev musl-dev

COPY . /app/

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "furetracker.wsgi:application"]
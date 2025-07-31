# Используем официальный образ Python 3.12.4 на базе Debian Bookworm.
FROM python:3.12.4-slim-bookworm

# Устанавливаем рабочую директорию.
WORKDIR /app

# Настраиваем переменные окружения.
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Устанавливаем системные зависимости.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей и устанавливаем их.
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Копируем rest of the project
COPY . /app/

# Создаем директорию для логов и делаем entrypoint.sh исполняемым.
RUN mkdir -p /var/log/django/ && \
    chmod +x /app/entrypoint.sh

# Указываем, какой порт будет слушать приложение.
EXPOSE 8000

# Делаем наш скрипт точкой входа в контейнер.
ENTRYPOINT ["/app/entrypoint.sh"]

# Команда для запуска Gunicorn, которая будет передана в наш entrypoint.sh.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "furetracker.wsgi:application"]

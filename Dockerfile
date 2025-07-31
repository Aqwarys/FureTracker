# Используем официальный образ Python 3.12.4 на базе Debian Bookworm.
FROM python:3.12.4-slim-bookworm

# Устанавливаем рабочую директорию.
WORKDIR /app

# Настраиваем переменные окружения.
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Устанавливаем системные зависимости, включая netcat и dos2unix.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    netcat-traditional \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей и устанавливаем их.
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Копируем остальной код проекта.
COPY . /app/

# Конвертируем entrypoint.sh в формат Unix и делаем его исполняемым.
RUN dos2unix /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Создаем директорию для логов.
RUN mkdir -p /var/log/django/

# Указываем, какой порт будет слушать приложение.
EXPOSE 8000

# Делаем наш скрипт точкой входа в контейнер.
ENTRYPOINT ["/app/entrypoint.sh"]

# Команда для запуска Gunicorn.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "furetracker.wsgi:application"]

FROM python:3.11-slim

# Установка nginx и компилятора для uwsgi
RUN apt-get update && apt-get install -y \
    nginx \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /var/log/uwsgi /run

WORKDIR /app

# Копируем зависимости
COPY requirements/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем приложение
COPY app/ ./app/
COPY wsgi.py .
COPY uwsgi.ini /etc/uwsgi.ini
COPY nginx/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

# Запускаем uwsgi в фоне, затем nginx
CMD uwsgi --ini /etc/uwsgi.ini --daemonize /var/log/uwsgi.log && nginx -g 'daemon off;'

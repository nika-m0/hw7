FROM python:3.11-slim

# Установка nginx
RUN apt-get update && apt-get install -y nginx && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /var/log/uwsgi

WORKDIR /app

# Копируем зависимости
COPY requirements/ ./requirements/
RUN pip install --no-cache-dir -r requirements/prod.txt

# Копируем приложение
COPY app/ ./app/
COPY wsgi.py .

# Копируем конфиги
COPY uwsgi.ini /etc/uwsgi.ini
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# Создаём директорию для статики
RUN mkdir -p /app/app/static

# Создаём пользователя www-data если нет (обычно уже есть)
RUN id -u www-data 2>/dev/null || useradd -r -s /bin/false www-data

EXPOSE 80

# Запуск uwsgi в фоне и nginx на переднем плане
CMD uwsgi --ini /etc/uwsgi.ini && nginx -g 'daemon off;'
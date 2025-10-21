# 🚀 Руководство по развертыванию KinoSite

Пошаговая инструкция по развертыванию проекта на production сервере.

## 📋 Содержание

- [Подготовка сервера](#подготовка-сервера)
- [Установка зависимостей](#установка-зависимостей)
- [Настройка PostgreSQL](#настройка-postgresql)
- [Настройка Redis](#настройка-redis)
- [Настройка Django](#настройка-django)
- [Настройка Gunicorn](#настройка-gunicorn)
- [Настройка Nginx](#настройка-nginx)
- [SSL сертификат](#ssl-сертификат)
- [Автозапуск](#автозапуск)

---

## Подготовка сервера

### Требования к серверу:

- **OS**: Ubuntu 20.04/22.04 LTS (рекомендуется)
- **RAM**: минимум 2GB
- **Storage**: минимум 20GB
- **Python**: 3.8+

### Обновление системы:

```bash
sudo apt update
sudo apt upgrade -y
```

---

## Установка зависимостей

### 1. Python и pip

```bash
sudo apt install python3 python3-pip python3-venv -y
```

### 2. Git

```bash
sudo apt install git -y
```

### 3. Nginx

```bash
sudo apt install nginx -y
```

### 4. PostgreSQL

```bash
sudo apt install postgresql postgresql-contrib -y
```

### 5. Redis

```bash
sudo apt install redis-server -y
sudo systemctl enable redis-server
```

### 6. Системные зависимости для Python пакетов

```bash
sudo apt install python3-dev libpq-dev build-essential -y
```

---

## Настройка PostgreSQL

### 1. Создание базы данных и пользователя

```bash
sudo -u postgres psql

# В PostgreSQL консоли:
CREATE DATABASE kinosite_production;
CREATE USER kinouser WITH PASSWORD 'сильный_пароль_здесь';
ALTER ROLE kinouser SET client_encoding TO 'utf8';
ALTER ROLE kinouser SET default_transaction_isolation TO 'read committed';
ALTER ROLE kinouser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE kinosite_production TO kinouser;
\q
```

### 2. Настройка доступа

```bash
sudo nano /etc/postgresql/*/main/pg_hba.conf

# Добавьте строку:
local   all             kinouser                                md5

# Перезапустите PostgreSQL:
sudo systemctl restart postgresql
```

---

## Настройка Redis

```bash
# Проверка статуса
sudo systemctl status redis

# Настройка (опционально)
sudo nano /etc/redis/redis.conf

# Рекомендуемые настройки:
# maxmemory 256mb
# maxmemory-policy allkeys-lru

sudo systemctl restart redis
```

---

## Настройка Django

### 1. Клонирование проекта

```bash
cd /var/www/
sudo mkdir kinosite
sudo chown $USER:$USER kinosite
cd kinosite

git clone your-repository-url .
# или загрузите файлы вручную
```

### 2. Создание виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Настройка .env для production

```bash
nano .env
```

Содержимое:

```env
# Django
SECRET_KEY=генерируйте_новый_секретный_ключ
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-server-ip

# Database
DB_NAME=kinosite_production
DB_USER=kinouser
DB_PASSWORD=сильный_пароль_здесь
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://127.0.0.1:6379/1

# Остальные настройки...
```

### 5. Генерация SECRET_KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 6. Миграции и статика

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 7. Создание директорий для медиа

```bash
mkdir -p media/posters media/backdrops media/persons media/news media/avatars
sudo chown -R www-data:www-data media/
sudo chmod -R 755 media/
```

---

## Настройка Gunicorn

### 1. Создание systemd service

```bash
sudo nano /etc/systemd/system/kinosite.service
```

Содержимое:

```ini
[Unit]
Description=KinoSite Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/kinosite
Environment="PATH=/var/www/kinosite/venv/bin"
ExecStart=/var/www/kinosite/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/var/www/kinosite/kinosite.sock \
          --access-logfile /var/log/kinosite/access.log \
          --error-logfile /var/log/kinosite/error.log \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 2. Создание директорий для логов

```bash
sudo mkdir -p /var/log/kinosite
sudo chown www-data:www-data /var/log/kinosite
```

### 3. Настройка прав

```bash
sudo chown -R www-data:www-data /var/www/kinosite
```

### 4. Запуск Gunicorn

```bash
sudo systemctl start kinosite
sudo systemctl enable kinosite
sudo systemctl status kinosite
```

---

## Настройка Nginx

### 1. Создание конфигурации

```bash
sudo nano /etc/nginx/sites-available/kinosite
```

Содержимое:

```nginx
upstream kinosite_server {
    server unix:/var/www/kinosite/kinosite.sock fail_timeout=0;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    client_max_body_size 100M;
    
    # Логи
    access_log /var/log/nginx/kinosite_access.log;
    error_log /var/log/nginx/kinosite_error.log;
    
    # Статика
    location /static/ {
        alias /var/www/kinosite/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Медиа
    location /media/ {
        alias /var/www/kinosite/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
    
    # Robots.txt
    location /robots.txt {
        alias /var/www/kinosite/static/robots.txt;
    }
    
    # Favicon
    location /favicon.ico {
        alias /var/www/kinosite/static/images/favicon.png;
    }
    
    # Основное приложение
    location / {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        
        if (!-f $request_filename) {
            proxy_pass http://kinosite_server;
            break;
        }
    }
    
    # Сжатие
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript;
}
```

### 2. Активация конфигурации

```bash
sudo ln -s /etc/nginx/sites-available/kinosite /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 3. Настройка firewall

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

---

## SSL сертификат (Let's Encrypt)

### 1. Установка Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

### 2. Получение сертификата

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 3. Автоматическое обновление

```bash
sudo systemctl status certbot.timer
```

Certbot автоматически обновит сертификат.

---

## Автозапуск

### Celery (для фоновых задач)

Создайте systemd service для Celery:

```bash
sudo nano /etc/systemd/system/celery.service
```

```ini
[Unit]
Description=Celery Service
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/var/www/kinosite
Environment="PATH=/var/www/kinosite/venv/bin"
ExecStart=/var/www/kinosite/venv/bin/celery -A config multi start worker \
          --pidfile=/var/run/celery/%n.pid \
          --logfile=/var/log/celery/%n%I.log \
          --loglevel=INFO

[Install]
WantedBy=multi-user.target
```

```bash
sudo mkdir -p /var/run/celery /var/log/celery
sudo chown www-data:www-data /var/run/celery /var/log/celery

sudo systemctl start celery
sudo systemctl enable celery
```

---

## Мониторинг и обслуживание

### Просмотр логов

```bash
# Gunicorn логи
sudo tail -f /var/log/kinosite/error.log

# Nginx логи
sudo tail -f /var/log/nginx/kinosite_error.log

# Celery логи
sudo tail -f /var/log/celery/worker.log
```

### Перезапуск сервисов

```bash
# После обновления кода
sudo systemctl restart kinosite

# Nginx
sudo systemctl restart nginx

# Celery
sudo systemctl restart celery
```

### Backup базы данных

```bash
# Создание backup
pg_dump -U kinouser kinosite_production > backup_$(date +%Y%m%d).sql

# Восстановление
psql -U kinouser kinosite_production < backup_20240101.sql
```

### Обновление проекта

```bash
cd /var/www/kinosite
source venv/bin/activate

# Получить обновления
git pull origin main

# Обновить зависимости
pip install -r requirements.txt

# Миграции
python manage.py migrate

# Статика
python manage.py collectstatic --noinput

# Перезапуск
sudo systemctl restart kinosite
```

---

## Оптимизация производительности

### 1. PostgreSQL

```bash
sudo nano /etc/postgresql/*/main/postgresql.conf

# Рекомендуемые настройки для 2GB RAM:
shared_buffers = 512MB
effective_cache_size = 1536MB
maintenance_work_mem = 128MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
```

### 2. Redis

```bash
sudo nano /etc/redis/redis.conf

maxmemory 512mb
maxmemory-policy allkeys-lru
```

### 3. Gunicorn workers

Оптимальное количество workers:
```
workers = (2 * CPU_CORES) + 1
```

---

## Безопасность

### 1. Скрыть версию Nginx

```bash
sudo nano /etc/nginx/nginx.conf

# В секции http:
server_tokens off;
```

### 2. Fail2ban для защиты от брутфорса

```bash
sudo apt install fail2ban -y

sudo nano /etc/fail2ban/jail.local
```

```ini
[nginx-limit-req]
enabled = true

[nginx-botsearch]
enabled = true
```

```bash
sudo systemctl restart fail2ban
```

### 3. Регулярные обновления

```bash
# Настройте автоматические обновления безопасности
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

## Проверка работоспособности

1. Откройте https://yourdomain.com/
2. Проверьте админку: https://yourdomain.com/admin/
3. Проверьте загрузку статики и медиа
4. Проверьте работу форм (регистрация, комментарии)
5. Проверьте SSL сертификат

---

## Troubleshooting

### Ошибка 502 Bad Gateway

```bash
# Проверьте статус Gunicorn
sudo systemctl status kinosite

# Проверьте логи
sudo tail -f /var/log/kinosite/error.log

# Проверьте права на socket
ls -la /var/www/kinosite/kinosite.sock
```

### Статика не загружается

```bash
# Пересоберите статику
python manage.py collectstatic --clear --noinput

# Проверьте права
sudo chown -R www-data:www-data /var/www/kinosite/staticfiles/
```

### База данных не подключается

```bash
# Проверьте PostgreSQL
sudo systemctl status postgresql

# Проверьте подключение
psql -U kinouser -d kinosite_production -h localhost
```

---

**Успешного деплоя! 🚀**


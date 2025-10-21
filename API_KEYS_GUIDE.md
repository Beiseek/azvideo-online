# 🔑 Руководство по получению API ключей

Это подробное пошаговое руководство по получению всех необходимых API ключей для проекта KinoSite.

## 📊 Список необходимых API ключей

| Сервис | Обязательность | Назначение |
|--------|---------------|------------|
| PostgreSQL | ✅ Обязательно | База данных |
| Redis | ✅ Обязательно | Кэширование |
| TMDB API | ⭐ Рекомендуется | Данные о фильмах |
| Google ReCAPTCHA | ⭐ Рекомендуется | Защита от спама |
| Google OAuth2 | 🔵 Опционально | Вход через Google |
| Facebook OAuth | 🔵 Опционально | Вход через Facebook |
| GeoIP2 | 🔵 Опционально | Определение языка по IP |
| Google Analytics | 🔵 Опционально | Аналитика |
| SMTP (Email) | 🔵 Опционально | Уведомления |

---

## 1️⃣ PostgreSQL Database (ОБЯЗАТЕЛЬНО)

### Windows:

1. **Скачайте PostgreSQL**
   - Перейдите на https://www.postgresql.org/download/windows/
   - Скачайте установщик (рекомендуется версия 14+)

2. **Установка**
   - Запустите установщик
   - Запомните пароль для пользователя `postgres`
   - Порт по умолчанию: `5432`

3. **Создайте базу данных**
   ```cmd
   # Откройте командную строку и войдите в PostgreSQL
   psql -U postgres
   
   # Создайте базу данных
   CREATE DATABASE kinosite_db;
   
   # Выход
   \q
   ```

4. **Настройте .env**
   ```env
   DB_NAME=kinosite_db
   DB_USER=postgres
   DB_PASSWORD=ваш_пароль_здесь
   DB_HOST=localhost
   DB_PORT=5432
   ```

### Linux (Ubuntu/Debian):

```bash
# Установка PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Создание базы данных
sudo -u postgres psql
CREATE DATABASE kinosite_db;
CREATE USER kinouser WITH PASSWORD 'your_password';
ALTER DATABASE kinosite_db OWNER TO kinouser;
GRANT ALL PRIVILEGES ON DATABASE kinosite_db TO kinouser;
\q

# Настройка .env
DB_NAME=kinosite_db
DB_USER=kinouser
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

---

## 2️⃣ Redis (ОБЯЗАТЕЛЬНО)

### Windows:

1. **Скачайте Redis для Windows**
   - GitHub: https://github.com/microsoftarchive/redis/releases
   - Скачайте `Redis-x64-xxx.zip`

2. **Установка**
   - Распакуйте архив в `C:\Redis`
   - Запустите `redis-server.exe`

3. **Проверка**
   ```cmd
   redis-cli ping
   # Должен вернуть: PONG
   ```

4. **Настройка .env**
   ```env
   REDIS_URL=redis://127.0.0.1:6379/1
   ```

### Linux:

```bash
# Установка
sudo apt install redis-server

# Запуск
sudo systemctl start redis
sudo systemctl enable redis

# Проверка
redis-cli ping

# Настройка .env
REDIS_URL=redis://127.0.0.1:6379/1
```

---

## 3️⃣ TMDB API (Рекомендуется)

**Зачем**: Автоматическое получение данных о фильмах, постеров, трейлеров

### Пошаговая инструкция:

1. **Регистрация**
   - Перейдите на https://www.themoviedb.org/
   - Нажмите "Join TMDB"
   - Заполните форму регистрации

2. **Получение API ключа**
   - Войдите в аккаунт
   - Перейдите в Settings (в меню профиля)
   - Выберите "API" в левом меню
   - Нажмите "Create" или "Request an API Key"

3. **Заполнение формы**
   - Type of Use: выберите "Developer"
   - Application Name: `KinoSite`
   - Application URL: `http://localhost:8000` (для разработки)
   - Application Summary: `Movie database website for educational purposes`

4. **Получите ключ**
   - После одобрения вы получите API Key (v3 auth)
   - Скопируйте его

5. **Настройка .env**
   ```env
   TMDB_API_KEY=ваш_tmdb_api_ключ_здесь
   ```

### Пример использования (опционально):

```python
# В Django shell
from movies.utils import get_movie_from_tmdb
movie_data = get_movie_from_tmdb(550)  # Fight Club
```

---

## 4️⃣ Google ReCAPTCHA (Рекомендуется)

**Зачем**: Защита форм от спама и ботов

### Пошаговая инструкция:

1. **Перейдите на сайт**
   - https://www.google.com/recaptcha/admin

2. **Создайте новый сайт**
   - Label: `KinoSite`
   - reCAPTCHA type: выберите "reCAPTCHA v2" → "I'm not a robot" Checkbox
   
3. **Домены**
   Для разработки добавьте:
   - `localhost`
   - `127.0.0.1`
   
   Для продакшена:
   - `yourdomain.com`
   - `www.yourdomain.com`

4. **Получите ключи**
   - Site Key (публичный ключ)
   - Secret Key (приватный ключ)

5. **Настройка .env**
   ```env
   RECAPTCHA_PUBLIC_KEY=ваш_публичный_ключ
   RECAPTCHA_PRIVATE_KEY=ваш_приватный_ключ
   ```

---

## 5️⃣ Google OAuth2 (Опционально)

**Зачем**: Авторизация через аккаунт Google

### Пошаговая инструкция:

1. **Google Cloud Console**
   - Перейдите на https://console.cloud.google.com/

2. **Создайте проект**
   - Нажмите "Select a project" → "New Project"
   - Project name: `KinoSite`
   - Нажмите "Create"

3. **Включите Google+ API**
   - Перейдите в "APIs & Services" → "Library"
   - Найдите "Google+ API"
   - Нажмите "Enable"

4. **Создайте OAuth credentials**
   - "APIs & Services" → "Credentials"
   - "Create Credentials" → "OAuth client ID"
   - Application type: "Web application"
   - Name: `KinoSite OAuth`

5. **Authorized redirect URIs**
   Для разработки:
   ```
   http://127.0.0.1:8000/accounts/google/login/callback/
   http://localhost:8000/accounts/google/login/callback/
   ```
   
   Для продакшена:
   ```
   https://yourdomain.com/accounts/google/login/callback/
   ```

6. **Получите credentials**
   - Client ID
   - Client Secret

7. **Настройка .env**
   ```env
   GOOGLE_CLIENT_ID=ваш_client_id.apps.googleusercontent.com
   GOOGLE_SECRET=ваш_client_secret
   ```

---

## 6️⃣ Facebook OAuth (Опционально)

**Зачем**: Авторизация через Facebook

### Пошаговая инструкция:

1. **Facebook for Developers**
   - https://developers.facebook.com/
   - Войдите в аккаунт Facebook

2. **Создайте приложение**
   - "My Apps" → "Create App"
   - Use case: "None" (или "Other")
   - App Type: "Business"
   - Display Name: `KinoSite`

3. **Добавьте Facebook Login**
   - В дашборде приложения
   - "Add Product" → "Facebook Login" → "Set Up"

4. **Настройте OAuth**
   - Settings → Basic
   - App Domains: `localhost` (для разработки)
   
5. **Valid OAuth Redirect URIs**
   ```
   http://localhost:8000/accounts/facebook/login/callback/
   https://yourdomain.com/accounts/facebook/login/callback/
   ```

6. **Получите credentials**
   - App ID
   - App Secret (нажмите "Show" чтобы увидеть)

7. **Настройка .env**
   ```env
   FACEBOOK_APP_ID=ваш_app_id
   FACEBOOK_SECRET=ваш_app_secret
   ```

8. **Режим разработки**
   - По умолчанию приложение в "Development mode"
   - Для продакшена переключите в "Live mode"

---

## 7️⃣ GeoIP2 (Опционально)

**Зачем**: Автоматическое определение языка пользователя по IP

### Пошаговая инструкция:

1. **Регистрация на MaxMind**
   - https://www.maxmind.com/en/geolite2/signup

2. **Подтвердите email**

3. **Войдите в аккаунт**
   - https://www.maxmind.com/en/account/login

4. **Скачайте базу данных**
   - "Manage License Keys" → "Create new license key"
   - Или перейдите сразу к загрузке: https://www.maxmind.com/en/accounts/current/geoip/downloads
   - Скачайте "GeoLite2 Country" в формате MMDB

5. **Установка базы**
   ```bash
   # Создайте папку
   mkdir geoip
   
   # Распакуйте скачанный архив
   # Скопируйте GeoLite2-Country.mmdb в папку geoip/
   ```

6. **Структура проекта**
   ```
   kinosait/
   ├── geoip/
   │   └── GeoLite2-Country.mmdb
   ├── manage.py
   └── ...
   ```

7. **Настройка .env**
   ```env
   GEOIP_PATH=geoip
   ```

---

## 8️⃣ Email (SMTP) - Gmail (Опционально)

**Зачем**: Отправка уведомлений, восстановление пароля

### Для Gmail:

1. **Включите 2-Step Verification**
   - https://myaccount.google.com/security
   - "2-Step Verification" → "Get Started"

2. **Создайте App Password**
   - https://myaccount.google.com/apppasswords
   - Select app: "Mail"
   - Select device: "Other" → введите "Django KinoSite"
   - Нажмите "Generate"
   - **Сохраните 16-символьный пароль**

3. **Настройка .env**
   ```env
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=ваш_email@gmail.com
   EMAIL_HOST_PASSWORD=ваш_app_password_без_пробелов
   EMAIL_USE_TLS=True
   ```

### Для других провайдеров:

**Yandex:**
```env
EMAIL_HOST=smtp.yandex.ru
EMAIL_PORT=587
EMAIL_HOST_USER=ваш_email@yandex.ru
EMAIL_HOST_PASSWORD=ваш_пароль
EMAIL_USE_TLS=True
```

**Mail.ru:**
```env
EMAIL_HOST=smtp.mail.ru
EMAIL_PORT=465
EMAIL_HOST_USER=ваш_email@mail.ru
EMAIL_HOST_PASSWORD=ваш_пароль
EMAIL_USE_SSL=True
```

---

## 9️⃣ Google Analytics (Опционально)

**Зачем**: Отслеживание посещаемости и поведения пользователей

### Пошаговая инструкция:

1. **Google Analytics**
   - https://analytics.google.com/

2. **Создайте аккаунт**
   - Admin → "Create Account"
   - Account name: `KinoSite`

3. **Создайте свойство**
   - Property name: `KinoSite Website`
   - Time zone: выберите ваш часовой пояс
   - Currency: выберите валюту

4. **Получите Measurement ID**
   - После создания свойства
   - Скопируйте "Measurement ID" (формат: `G-XXXXXXXXXX`)

5. **Настройка .env**
   ```env
   GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
   ```

---

## ✅ Проверка настроек

### Полный .env файл должен выглядеть так:

```env
# Django
SECRET_KEY=your-very-long-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (ОБЯЗАТЕЛЬНО)
DB_NAME=kinosite_db
DB_USER=postgres
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Redis (ОБЯЗАТЕЛЬНО)
REDIS_URL=redis://127.0.0.1:6379/1

# TMDB API (Рекомендуется)
TMDB_API_KEY=your_tmdb_api_key

# ReCAPTCHA (Рекомендуется)
RECAPTCHA_PUBLIC_KEY=your_recaptcha_public_key
RECAPTCHA_PRIVATE_KEY=your_recaptcha_private_key

# Google OAuth (Опционально)
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_SECRET=your_client_secret

# Facebook OAuth (Опционально)
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_SECRET=your_facebook_secret

# GeoIP (Опционально)
GEOIP_PATH=geoip

# Email (Опционально)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
EMAIL_USE_TLS=True

# Analytics (Опционально)
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
```

---

## 🔍 Тестирование

После настройки всех ключей:

```bash
# Запустите сервер
python manage.py runserver

# Проверьте:
# - Вход через Google/Facebook работает
# - ReCAPTCHA появляется на формах
# - Email уведомления отправляются
# - Язык определяется автоматически
```

---

## ⚠️ Безопасность

1. **Никогда не коммитьте .env файл в Git**
   - Добавьте `.env` в `.gitignore`

2. **Используйте сильный SECRET_KEY**
   ```python
   # Генерация в Django shell
   from django.core.management.utils import get_random_secret_key
   print(get_random_secret_key())
   ```

3. **В продакшене**
   - Установите `DEBUG=False`
   - Используйте HTTPS
   - Обновите ALLOWED_HOSTS
   - Используйте переменные окружения сервера

---

## 📞 Помощь

Если возникли проблемы:
1. Проверьте правильность ключей в `.env`
2. Убедитесь что сервисы (PostgreSQL, Redis) запущены
3. Проверьте логи Django: `python manage.py runserver`
4. Проверьте redirect URIs для OAuth (должны точно совпадать)

**Успехов в разработке! 🚀**


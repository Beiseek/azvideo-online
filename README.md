# 🎬 KinoSite - Профессиональный кино-портал

Современный кино-сайт на Django с поддержкой двух языков (узбекский/азербайджанский), темной темой в стиле Netflix и полным функционалом для управления фильмами и сериалами.

## 📋 Возможности

- ✅ **Каталог контента** - фильмы, сериалы, мультфильмы с мощной системой фильтрации
- ✅ **Многоязычность** - поддержка узбекского и азербайджанского языков с автоопределением по IP
- ✅ **Современный дизайн** - темная тема в стиле Netflix с адаптивной версткой
- ✅ **Пользовательские функции** - рейтинги, комментарии, избранное, списки просмотра
- ✅ **REST API** - полноценный API для интеграций
- ✅ **Социальная авторизация** - вход через Google и Facebook
- ✅ **SEO оптимизация** - sitemap, schema.org разметка, мета-теги
- ✅ **Админ-панель** - расширенная панель управления с inline формами
- ✅ **Кэширование** - Redis для высокой производительности
- ✅ **Безопасность** - защита от XSS, SQL-инъекций, CAPTCHA, HTTPS

## 🛠 Технологический стек

- **Backend**: Django 4.2, Django REST Framework
- **Frontend**: Bootstrap 5, jQuery, Font Awesome
- **База данных**: PostgreSQL
- **Кэширование**: Redis
- **Медиа**: Pillow, django-imagekit
- **API интеграции**: TMDB API, GeoIP2
- **Аутентификация**: django-allauth, JWT

## 📦 Установка и настройка

### 1. Клонирование и создание виртуального окружения

```bash
cd kinosait
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Настройка переменных окружения

Создайте файл `.env` на основе `.env.example`:

```bash
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

Заполните `.env` файл:

```env
# Django
SECRET_KEY=ваш-секретный-ключ-здесь
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL
DB_NAME=kinosite_db
DB_USER=postgres
DB_PASSWORD=ваш_пароль
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://127.0.0.1:6379/1

# См. далее инструкции по получению API ключей
```

### 4. Установка PostgreSQL

#### Windows:
1. Скачайте PostgreSQL с [официального сайта](https://www.postgresql.org/download/windows/)
2. Установите и запомните пароль для пользователя `postgres`
3. Создайте базу данных:

```sql
CREATE DATABASE kinosite_db;
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo -u postgres psql
CREATE DATABASE kinosite_db;
CREATE USER kinouser WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE kinosite_db TO kinouser;
\q
```

### 5. Установка Redis

#### Windows:
1. Скачайте Redis для Windows: https://github.com/microsoftarchive/redis/releases
2. Распакуйте и запустите `redis-server.exe`

#### Linux:
```bash
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

### 6. Миграции базы данных

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Создание суперпользователя

```bash
python manage.py createsuperuser
```

### 8. Запуск сервера разработки

```bash
python manage.py runserver
```

Сайт будет доступен по адресу: http://127.0.0.1:8000/
Админ-панель: http://127.0.0.1:8000/admin/

## 🔑 Получение API ключей

### 1. TMDB API (для данных о фильмах)

**Зачем нужен**: Получение информации о фильмах, постеров, трейлеров

**Как получить**:
1. Зарегистрируйтесь на https://www.themoviedb.org/
2. Перейдите в Settings → API
3. Запросите API ключ (выберите "Developer")
4. Заполните форму (можно указать учебный проект)
5. Скопируйте API Key (v3 auth) в `.env`:

```env
TMDB_API_KEY=ваш_ключ_здесь
```

### 2. Google ReCAPTCHA (защита от спама)

**Зачем нужен**: Защита форм комментариев и регистрации

**Как получить**:
1. Перейдите на https://www.google.com/recaptcha/admin
2. Зарегистрируйте новый сайт
3. Выберите reCAPTCHA v2 (Checkbox)
4. Домены: `localhost`, `127.0.0.1` (для разработки)
5. Скопируйте ключи:

```env
RECAPTCHA_PUBLIC_KEY=ваш_публичный_ключ
RECAPTCHA_PRIVATE_KEY=ваш_приватный_ключ
```

### 3. Google OAuth2 (авторизация через Google)

**Зачем нужен**: Вход через аккаунт Google

**Как получить**:
1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект
3. Включите "Google+ API"
4. Credentials → Create Credentials → OAuth 2.0 Client ID
5. Application type: Web application
6. Authorized redirect URIs: `http://127.0.0.1:8000/accounts/google/login/callback/`
7. Скопируйте Client ID и Client Secret:

```env
GOOGLE_CLIENT_ID=ваш_client_id
GOOGLE_SECRET=ваш_secret
```

### 4. Facebook OAuth (авторизация через Facebook)

**Зачем нужен**: Вход через аккаунт Facebook

**Как получить**:
1. Перейдите на [Facebook for Developers](https://developers.facebook.com/)
2. Создайте новое приложение
3. Добавьте продукт "Facebook Login"
4. Settings → Basic → скопируйте App ID и App Secret
5. Valid OAuth Redirect URIs: `http://127.0.0.1:8000/accounts/facebook/login/callback/`

```env
FACEBOOK_APP_ID=ваш_app_id
FACEBOOK_SECRET=ваш_secret
```

### 5. GeoIP2 (определение страны по IP)

**Зачем нужен**: Автоматическое определение языка пользователя

**Как получить**:
1. Зарегистрируйтесь на https://www.maxmind.com/en/geolite2/signup
2. Скачайте GeoLite2 Country database (MMDB format)
3. Создайте папку `geoip` в корне проекта
4. Распакуйте `GeoLite2-Country.mmdb` в эту папку

```
kinosait/
├── geoip/
│   └── GeoLite2-Country.mmdb
```

### 6. Email настройки (для уведомлений)

**Gmail**:
1. Включите "2-Step Verification" в настройках Google аккаунта
2. Создайте "App Password": https://myaccount.google.com/apppasswords
3. Используйте этот пароль:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=ваш_email@gmail.com
EMAIL_HOST_PASSWORD=app_password_здесь
EMAIL_USE_TLS=True
```

### 7. Google Analytics (опционально)

**Как получить**:
1. Создайте аккаунт на https://analytics.google.com/
2. Создайте свойство для сайта
3. Скопируйте Measurement ID:

```env
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
```

## 📁 Структура проекта

```
kinosait/
├── config/              # Настройки Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/               # Основное приложение
│   ├── middleware.py
│   └── context_processors.py
├── movies/             # Приложение фильмов
│   ├── models.py       # Модели (Movie, Series, Genre, etc.)
│   ├── views.py        # Представления
│   ├── admin.py        # Админ-панель
│   ├── serializers.py  # REST API сериализаторы
│   └── api_views.py    # API endpoints
├── users/              # Приложение пользователей
│   ├── models.py       # UserProfile, UserActivity
│   ├── views.py
│   └── forms.py
├── templates/          # HTML шаблоны
│   ├── base.html
│   ├── movies/
│   └── users/
├── static/             # Статические файлы
│   ├── css/
│   ├── js/
│   └── images/
├── media/              # Загруженные файлы
├── requirements.txt
└── .env.example
```

## 🚀 Развертывание в production

### Подготовка

1. Обновите `.env`:
```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

2. Соберите статические файлы:
```bash
python manage.py collectstatic
```

3. Настройте Gunicorn:
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

4. Настройте Nginx как reverse proxy

5. Настройте SSL сертификат (Let's Encrypt)

## 📝 Использование

### Добавление контента через админку

1. Войдите в админ-панель: `/admin/`
2. Добавьте жанры, страны, персон
3. Создайте фильм или сериал
4. Для сериалов добавьте сезоны и эпизоды через inline формы
5. Отметьте "Рекомендуемое" для показа в слайдере на главной

### API Endpoints

- `GET /api/movies/` - список фильмов
- `GET /api/movies/{id}/` - детали фильма
- `POST /api/movies/{id}/rate/` - оценить фильм
- `GET /api/series/` - список сериалов
- `POST /api/comments/` - добавить комментарий
- `POST /api/favorites/toggle/` - добавить/удалить из избранного

## 🎨 Кастомизация дизайна

Основные стили находятся в `static/css/style.css`. Цветовая схема:

```css
--primary-color: #E50914;      /* Красный акцент */
--background-dark: #121212;    /* Темный фон */
--background-light: #181818;   /* Светлее фон */
--text-white: #FFFFFF;         /* Белый текст */
```

## 📊 Модели данных

### Основные модели:

- **Movie** - фильмы
- **Series** - сериалы
- **Season** - сезоны сериалов
- **Episode** - эпизоды
- **Genre** - жанры
- **Country** - страны
- **Person** - актеры/режиссеры
- **Rating** - оценки пользователей
- **Comment** - комментарии с древовидной структурой
- **UserProfile** - профили пользователей
- **News** - новости кино

## 🔧 Troubleshooting

### Проблема с PostgreSQL подключением
```bash
# Проверьте статус PostgreSQL
# Windows: Services → PostgreSQL
# Linux: sudo systemctl status postgresql
```

### Redis не подключается
```bash
# Проверьте запущен ли Redis
redis-cli ping
# Должен вернуть: PONG
```

### Ошибки миграций
```bash
python manage.py migrate --run-syncdb
```

### Проблемы с медиа файлами
Убедитесь что папки `media/` и `static/` существуют и доступны для записи

## 📞 Поддержка

При возникновении вопросов:
1. Проверьте логи Django
2. Убедитесь что все зависимости установлены
3. Проверьте `.env` файл
4. Проверьте что PostgreSQL и Redis запущены

## 📄 Лицензия

MIT License - свободно используйте для своих проектов

## 🎯 Roadmap

- [ ] Интеграция с видео-плеерами
- [ ] Автоматический парсинг контента
- [ ] Мобильное приложение
- [ ] Подписки и платные функции
- [ ] Рекомендательная система на основе ML
- [ ] Интеграция с Telegram ботом

---

**Создано с ❤️ для любителей кино**


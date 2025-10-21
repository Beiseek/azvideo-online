# 🚀 Быстрый старт KinoSite

Краткое руководство для быстрого запуска проекта.

## ⚡ Минимальная установка (5 минут)

### 1. Установите зависимости

```bash
# Создайте виртуальное окружение
python -m venv venv

# Активируйте (Windows)
venv\Scripts\activate

# Активируйте (Linux/Mac)
source venv/bin/activate

# Установите пакеты
pip install -r requirements.txt
```

### 2. Установите PostgreSQL

**Windows:**
- Скачайте: https://www.postgresql.org/download/windows/
- Установите с паролем для пользователя `postgres`
- Создайте базу данных:
  ```sql
  psql -U postgres
  CREATE DATABASE kinosite_db;
  \q
  ```

**Linux:**
```bash
sudo apt install postgresql
sudo -u postgres psql -c "CREATE DATABASE kinosite_db;"
```

### 3. Установите Redis

**Windows:**
- Скачайте: https://github.com/microsoftarchive/redis/releases
- Распакуйте и запустите `redis-server.exe`

**Linux:**
```bash
sudo apt install redis-server
sudo systemctl start redis
```

### 4. Настройте .env

Файл `.env` уже создан с базовыми настройками. Обновите только пароль PostgreSQL:

```env
DB_PASSWORD=ваш_пароль_postgres
```

### 5. Примените миграции

```bash
python manage.py migrate
```

### 6. Создайте суперпользователя

```bash
python manage.py createsuperuser
```

### 7. Запустите сервер

```bash
python manage.py runserver
```

✅ **Готово!** Откройте http://127.0.0.1:8000/

---

## 📝 Первые шаги

### Войдите в админку
- URL: http://127.0.0.1:8000/admin/
- Используйте данные суперпользователя

### Добавьте тестовые данные

1. **Создайте жанры:**
   - Movies → Genres → Add Genre
   - Примеры: Боевик, Драма, Комедия, Ужасы

2. **Создайте страны:**
   - Movies → Countries → Add Country
   - Примеры: Узбекистан (UZ), США (US), Корея (KR)

3. **Добавьте актеров/режиссеров:**
   - Movies → Persons → Add Person
   - Укажите имя и роль (actor/director)

4. **Создайте фильм:**
   - Movies → Movies → Add Movie
   - Заполните:
     - Название (UZ и AZ)
     - Описание
     - Постер (загрузите картинку)
     - Год, жанры, страны
     - Отметьте "Рекомендуемое" для показа в слайдере

### Протестируйте функции

- ✅ Главная страница с слайдером
- ✅ Каталог фильмов с фильтрами
- ✅ Детальная страница фильма
- ✅ Поиск
- ✅ Регистрация и вход

---

## 🔑 Получение API ключей (опционально)

Для полного функционала получите API ключи. Подробная инструкция: [API_KEYS_GUIDE.md](API_KEYS_GUIDE.md)

### Приоритет:

1. **TMDB API** (рекомендуется) - данные о фильмах
   - Регистрация: https://www.themoviedb.org/
   - Получение ключа: Settings → API

2. **Google ReCAPTCHA** (рекомендуется) - защита от спама
   - https://www.google.com/recaptcha/admin

3. **OAuth (опционально)** - вход через соц.сети
   - Google: https://console.cloud.google.com/
   - Facebook: https://developers.facebook.com/

---

## 🎨 Кастомизация

### Изменить цветовую схему

Откройте `static/css/style.css` и измените переменные:

```css
:root {
    --primary-color: #E50914;      /* Красный → ваш цвет */
    --background-dark: #121212;    /* Фон */
}
```

### Изменить название сайта

В `core/context_processors.py`:

```python
'SITE_NAME': 'Ваше название',
```

---

## 📊 Структура проекта

```
kinosait/
├── config/          # Настройки Django
├── core/            # Основное приложение
├── movies/          # Фильмы и сериалы
├── users/           # Пользователи
├── templates/       # HTML шаблоны
├── static/          # CSS, JS, изображения
└── media/           # Загруженные файлы
```

---

## 🐛 Решение проблем

### PostgreSQL не подключается
```bash
# Проверьте статус
# Windows: Services → PostgreSQL
# Linux: sudo systemctl status postgresql
```

### Redis не работает
```bash
redis-cli ping
# Должен вернуть: PONG
```

### Ошибки миграций
```bash
python manage.py migrate --run-syncdb
```

### Статика не загружается
```bash
python manage.py collectstatic --noinput
```

---

## 📚 Дополнительно

- **Полная документация**: [README.md](README.md)
- **API ключи**: [API_KEYS_GUIDE.md](API_KEYS_GUIDE.md)
- **Deployment**: см. раздел "Развертывание" в README.md

---

## 🎯 Что дальше?

1. Заполните каталог контентом
2. Настройте социальную авторизацию
3. Добавьте Google Analytics
4. Настройте email уведомления
5. Деплой на сервер

**Удачи! 🚀**


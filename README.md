# 📦 platform_for_exchang

**Платформа обмена товарами между пользователями.**

## 🚀 Описание

Это веб-приложение на Django, позволяющее пользователям размещать объявления о своих товарах, просматривать чужие, предлагать обмен и принимать/отклонять предложения. Система поддерживает авторизацию через JWT и предоставляет административную панель для управления моделями.

---

## 🧩 Основной функционал

- 🔹 Регистрация и вход
- 🔹 Размещение и просмотр объявлений
- 🔹 Обмен товарами между пользователями
- 🔹 Управление входящими и исходящими предложениями: принятие, отказ и удаление
- 🔹 Создание запросов на обмен
- 🔹 Панель администратора

---

## ⚙️ Установка и запуск

1. **Клонировать репозиторий:**
   ```bash
   git clone https://github.com/your-username/platform_for_exchang.git
   cd platform_for_exchang
   ```

2. **Создать и активировать виртуальное окружение:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. **Установить зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Создать файл `.env` и указать переменные:**
   ```env
   DJANGO_SECRET_KEY=your_secret_key
   DJANGO_DEBUG=True
   DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=127.0.0.1
   DB_PORT=5432
   ```

5. **Запустить PostgreSQL в Docker:**
   ```bash
   docker-compose up -d
   ```

6. **Выполнить миграции и создать суперпользователя:**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

9. **Запустить сервер разработки:**
   ```bash
   python manage.py runserver
   ```

---

## 🧪 Тестирование

Тесты расположены в директории `platform_for_exchang/ads/tests`.

Запуск:
```bash
pytest
```

---

## 🔐 Аутентификация

Используется библиотека **`rest_framework_simplejwt`**:

- Поддержка регистрации/входа через API
- Авторизация через JWT-токены

---


## Взаимодействие
Веб-интерфейс: http://127.0.0.1:8000/ 
Панель администратора: http://127.0.0.1:8000/admin/ 
Redoc: http://127.0.0.1:8000/redoc/


---


## 🖼️ Интерфейс

Интерфейс реализован на чистом **HTML**, без использования фронтенд-фреймворков. Доступен минимальный UI для взаимодействия с платформой.

---

## 🛠️ Зависимости

- Django 5.2.1
- djangorestframework
- django-filter
- python-decouple
- psycopg2-binary
- simplejwt
- widget_tweaks
- pytest

---

## 📁 Структура проекта

```
platform_for_exchang/
├── ads/                   # Основное приложение
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   └── tests/
├── platform_for_exchang/ # Конфигурация проекта
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── templates/             # HTML-шаблоны
├── staticfiles/           # Собранная статика
├── manage.py
└── requirements.txt
```

---

## 🧑‍💻 Автор

**https://github.com/RedC0mrade**

---

## 📜 Лицензия

MIT License (или укажи свою)


PS. Наверное, статус в модели Excange стоило выполнить не через отдельную модель, а через
ENUM.
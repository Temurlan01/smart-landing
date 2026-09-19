# Developer Landing API

REST API для контактной формы лендинга разработчика с AI-анализом обращений, отправкой email, rate limiting и метриками.

> Backend pet-проект. Публичный demo URL не настроен — сервис запускается локально.

## Что это

API принимает обращения с лендинга и:

- валидирует имя, телефон, email и текст сообщения;
- сохраняет заявку в SQLite;
- определяет тональность и тип обращения;
- генерирует ответ через OpenAI;
- использует эвристический fallback без API-ключа или при ошибке AI;
- отправляет email-уведомления;
- ограничивает частоту запросов;
- предоставляет health check, метрики и Swagger UI.

## Зачем

Проект показывает, как организовать production-like backend для формы обратной связи: разделить views, services и repositories, безопасно интегрировать внешнюю AI-службу и сохранить работоспособность API при недоступности OpenAI.

## Стек

- **Python 3.9+**
- **Django 6.0.7**
- **Django REST Framework 3.17.1**
- **OpenAI API** — анализ и генерация ответа
- **SQLite** — хранение заявок
- **drf-spectacular** — OpenAPI/Swagger
- **django-cors-headers** — CORS
- **python-dotenv** — конфигурация
- **Postman Collection** — ручное тестирование

## Быстрый старт

```bash
git clone https://github.com/Temurlan01/smart-landing.git
cd smart-landing
python -m venv .venv

# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

В Windows скопируйте `.env.example` в `.env` вручную. Минимальная конфигурация:

```env
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
OPENAI_API_KEY=
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
RATE_LIMIT_REQUESTS=5
RATE_LIMIT_MINUTES=10
```

## Основные endpoints

| Метод | Endpoint | Назначение |
|---|---|---|
| `POST` | `/api/contact/` | Создать обращение |
| `GET` | `/api/health/` | Проверить состояние сервиса |
| `GET` | `/api/metrics/` | Получить агрегированные метрики |
| `GET` | `/api/docs/` | Swagger UI |
| `GET` | `/api/schema/` | OpenAPI schema |
| `GET` | `/admin/` | Django Admin |

Пример запроса:

```bash
curl -X POST http://127.0.0.1:8000/api/contact/ \\
  -H "Content-Type: application/json" \\
  -d '{"name":"Ivan","phone":"+71234567890","email":"ivan@example.com","comment":"Хочу обсудить сотрудничество по проекту."}'
```

## Архитектура

```text
api/
├── views/          # HTTP endpoints
├── serializers/    # валидация входных данных
├── services/       # AI, email, rate limit и метрики
├── repositories/   # работа с базой данных
├── models/         # ORM-модели
└── utils/          # validators, templates, logging
```

Используются Service Layer, Repository Pattern, middleware для логирования и graceful fallback для AI.

## Скриншоты и демо

Живое демо не опубликовано. После локального запуска откройте `/api/docs/` и добавьте скриншоты в `docs/screenshots/`:

```md
![Swagger UI](docs/screenshots/swagger.png)
![Успешная заявка](docs/screenshots/contact-response.png)
![Метрики](docs/screenshots/metrics.png)
```

Готовая коллекция запросов находится в [Postman_Collection.json](Postman_Collection.json).

## Документация

- [`.env.example`](.env.example)
- [`Postman_Collection.json`](Postman_Collection.json)
- [Swagger UI](http://127.0.0.1:8000/api/docs/)

## Лицензия

Лицензия пока не указана.

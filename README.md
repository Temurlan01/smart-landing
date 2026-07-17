# 🚀 Developer Landing API — Backend Test Task

Полнофункциональный **REST API сервис** для контактной формы лендинга разработчика с интеграцией AI (OpenAI), отправкой email-уведомлений, логированием и защитой от спама.

> ⚠️ **Деплой:** сервис не задеплоен на внешний хостинг. Ниже приведена подробная инструкция для **локального запуска** (Windows PowerShell), которая полностью заменяет деплой для целей проверки. Проект готов к деплою на Render/Railway — для этого достаточно добавить `gunicorn` в `requirements.txt`.

---

## 📋 Оглавление

1. [Как запустить проект](#1-как-запустить-проект)
2. [Стек технологий](#2-стек-технологий)
3. [Архитектура](#3-архитектура)
4. [Реализация API](#4-реализация-api)
5. [AI-интеграция](#5-ai-интеграция)
6. [Что сделано с помощью AI](#6-что-сделано-с-помощью-ai)
7. [Хранение данных](#7-хранение-данных)
8. [Примеры запросов (Postman / curl)](#8-примеры-запросов-postman--curl)
9. [Решение проблем (Troubleshooting)](#9-решение-проблем-troubleshooting)

---

## 1. Как запустить проект

### Требования

- **Windows 10/11** (PowerShell 5.1 или выше)
- **Python 3.9+**
- **pip** (входит в Python)

### Установка и запуск (пошагово)

**Шаг 1. Перейдите в папку проекта**

```powershell
cd C:\Users\user\Desktop\Test_Task1
```

**Шаг 2. Создайте виртуальное окружение**

```powershell
python -m venv .venv
```

**Шаг 3. Активируйте виртуальное окружение**

```powershell
.\.venv\Scripts\Activate.ps1
```

> ⚠️ Если возникнет ошибка **"Execution Policies"**, выполните:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> и повторите шаг 3.

**Шаг 4. Установите зависимости**

```powershell
pip install -r .\requirements.txt
```

**Шаг 5. Проверьте конфигурацию Django**

```powershell
python manage.py check
```

Ожидаемый вывод: `System check identified no issues (0 silenced).`

**Шаг 6. Примените миграции базы данных**

```powershell
python manage.py makemigrations
python manage.py migrate
```

**Шаг 7. (Опционально) Создайте суперпользователя**

```powershell
python manage.py createsuperuser
```

Введите `username`, `email` и пароль для доступа в `/admin/`.

**Шаг 8. Запустите сервер разработки**

```powershell
python manage.py runserver
```

Вывод:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### Переменные окружения (`.env`)

Создайте файл `.env` в **корне проекта**:

```env
# Безопасность
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Email (для разработки используется консоль)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@example.com
ADMIN_EMAIL=admin@example.com

# OpenAI (оставьте пустым для проверки fallback)
OPENAI_API_KEY=
OPENAI_MODEL=gpt-3.5-turbo

# Rate Limiting
RATE_LIMIT_REQUESTS=5
RATE_LIMIT_MINUTES=10

# Пути логирования
LOGS_DIR=logs
DATA_DIR=data
```

### Полезные URL после запуска

| URL | Описание |
|-----|---------|
| http://127.0.0.1:8000/api/docs/ | **Swagger UI** — интерактивная документация |
| http://127.0.0.1:8000/api/schema/ | OpenAPI JSON схема |
| http://127.0.0.1:8000/api/health/ | Health check |
| http://127.0.0.1:8000/api/metrics/ | Метрики |
| http://127.0.0.1:8000/admin/ | Django Admin |

---

## 2. Стек технологий

### Backend

| Компонент | Технология | Версия | Назначение |
|-----------|-----------|---------|-----------|
| Фреймворк | Django | 6.0.7 | Веб-фреймворк, ORM |
| API | Django REST Framework | 3.17.1 | REST API, сериализация, валидация |
| Документация | drf-spectacular | 0.30.0 | OpenAPI/Swagger генерация |
| CORS | django-cors-headers | 4.9.0 | Обработка CORS запросов |
| Environment | python-dotenv | 1.2.2 | Загрузка переменных окружения |
| База данных | SQLite3 | встроенная | Легковесное хранилище |

### AI

| Компонент | Технология | Версия | Назначение |
|-----------|-----------|---------|-----------|
| AI Provider | OpenAI | 2.46.0 | ChatGPT API для анализа текста |
| Fallback | Встроенная эвристика | — | Graceful fallback при недоступности AI |

### Логирование и мониторинг

- **Python logging** — встроенный модуль для логирования в файлы
- Файлы логов: `logs/api.log`, `logs/errors.log`

---

## 3. Архитектура

### Структура проекта

```
Test_Task1/
├── config/                      # Конфиг Django
│   ├── settings.py              # Основные настройки
│   ├── urls.py                  # Главный роутинг (включает api.urls)
│   ├── wsgi.py                  # WSGI приложение
│   └── asgi.py                  # ASGI приложение
├── api/                         # Основное приложение
│   ├── views/                   # Controllers
│   │   ├── contact_view.py      # API для контактной формы
│   │   ├── health_view.py       # Health check
│   │   └── metrics_view.py      # Статистика
│   ├── services/                # Бизнес-логика
│   │   ├── ai_service.py        # OpenAI интеграция
│   │   ├── email_service.py     # Отправка писем
│   │   ├── rate_limit_service.py# Защита от спама
│   │   └── metrics_service.py   # Сбор статистики
│   ├── repositories/            # Работа с БД
│   │   └── contact_repository.py# CRUD для Contact
│   ├── serializers/             # Валидация данных
│   │   └── contact_serializer.py# Схема контактной формы
│   ├── utils/                   # Вспомогательные функции
│   │   ├── email_templates.py   # Шаблоны писем
│   │   ├── validators.py        # Валидаторы
│   │   └── request_logger.py    # Логирование запросов
│   ├── models/                  # ORM модели
│   │   └── contact.py           # Модель ContactSubmission
│   ├── middleware.py            # Middleware для логирования
│   ├── exceptions.py            # Custom exception handler
│   ├── urls.py                  # API роутинг
│   ├── admin.py                 # Django Admin
│   └── apps.py                  # Конфиг приложения
├── logs/                        # Логи приложения (автосоздан)
├── data/                        # Данные (rate limit, метрики)
├── .env                         # Переменные окружения
├── requirements.txt             # Python зависимости
├── manage.py                    # Django CLI
└── README.md                    # Этот файл
```

### Паттерны проектирования

**1. Repository Pattern** (`api/repositories/contact_repository.py`)
Изолирует работу с БД от остального кода.

```python
# Вместо прямого использования ORM в views:
contact = ContactSubmission.objects.create(**data)

# Используем репозиторий:
contact = ContactRepository.create(**data)
```

**2. Service Layer Pattern** (`api/services/`)
Централизует бизнес-логику и интеграции (`ai_service.py`, `email_service.py`, `rate_limit_service.py`, `metrics_service.py`). View становится «худым»:

```python
class ContactView(APIView):
    def post(self, request):
        serializer = ContactCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = process_new_contact(serializer.validated_data)
        return Response(result, status=201)
```

**3. Exception Handler Pattern** (`api/exceptions.py`)
Все необработанные ошибки логируются и возвращают JSON `{"error": "..."}` вместо HTML traceback.

**4. Graceful Fallback Pattern** (`api/services/ai_service.py`)
При ошибке OpenAI сервис возвращает дефолтный ответ вместо падения.

**5. Middleware Pattern** (`api/middleware.py`)
Каждый запрос логируется до его обработки.

### Выбор технологий

| Технология | Почему |
|-----------|--------|
| Django + DRF | Стандарт для Python REST API, встроенная валидация, сериализация, документация |
| SQLite | Легковесная БД для разработки, не требует отдельного сервера |
| OpenAI | Мощный AI, простой API, хорошая документация |
| drf-spectacular | Автоматическая генерация Swagger/OpenAPI, стандарт в DRF |
| Слоистая архитектура | Стандартный паттерн в enterprise-приложениях, упрощает тестирование и масштабирование |

---

## 4. Реализация API

### Эндпоинты

**1) Отправка контактной формы**

```http
POST /api/contact/
Content-Type: application/json

{
  "name": "Иван Петров",
  "phone": "+71234567890",
  "email": "ivan@example.com",
  "comment": "Хочу обсудить сотрудничество по вашему проекту."
}
```

Успешный ответ (`201 Created`):
```json
{
  "message": "Thank you! Your message has been received.",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "sentiment": "positive",
  "request_type": "collaboration"
}
```

Ошибка валидации (`400 Bad Request`):
```json
{
  "name": ["This field is required."],
  "email": ["Enter a valid email address."],
  "comment": ["Ensure this field has at least 10 characters."]
}
```

Превышение rate limit (`429 Too Many Requests`):
```json
{
  "error": "Too many requests. Please try again later."
}
```

**2) Проверка статуса сервиса**

```http
GET /api/health/
```

Ответ (`200 OK`):
```json
{
  "status": "healthy",
  "message": "API is running",
  "version": "1.0.0"
}
```

**3) Получение статистики**

```http
GET /api/metrics/
```

Ответ (`200 OK`):
```json
{
  "total_submissions": 42,
  "by_sentiment": { "positive": 15, "neutral": 20, "negative": 7 },
  "by_type": { "inquiry": 10, "feedback": 15, "collaboration": 12, "support": 5 },
  "last_updated": "2024-07-17T15:30:00Z"
}
```

### Валидация входных данных

| Поле | Тип | Правила |
|------|-----|---------|
| `name` | string | 1–120 символов, только буквы и пробелы |
| `phone` | string | 9–15 цифр, может начинаться с `+` |
| `email` | string | Корректный email формат |
| `comment` | string | 10–5000 символов |

```python
class ContactSubmissionSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[EmailValidator()])
    phone = serializers.CharField(
        max_length=20,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', ...)]
    )

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise ValidationError("Минимум 2 символа")
        return value.strip()
```

### Обработка ошибок

Все ошибки логируются в `logs/api.log` и `logs/errors.log`:

```
ERROR 2024-07-17 15:30:45,123 api OpenAI API error: Connection timeout
INFO  2024-07-17 15:30:46,456 api Fallback sentiment analysis used
INFO  2024-07-17 15:30:47,789 api Contact created: 550e8400-e29b-41d4-a716-446655440000 from ivan@example.com
```

Используются статусы: `201 Created`, `400 Bad Request`, `429 Too Many Requests`, `500 Internal Server Error`. Все ответы — JSON, без HTML-трейсбеков (глобальный exception handler в `api/exceptions.py`).

---

## 5. AI-интеграция

### Используемые инструменты

- **OpenAI API** (ChatGPT 3.5-turbo)
- **Встроенная эвристика** (fallback)

### Функции AI

**1) Анализ тональности (Sentiment Analysis)**
```python
ai_result = ai_service.analyze_sentiment(comment)
# {'sentiment': 'positive'|'negative'|'neutral', 'score': 0.8, 'reasoning': '...'}
```

**2) Классификация типа запроса (Request Classification)**
```python
classification = ai_service.classify_request(comment)
# {'type': 'inquiry'|'feedback'|'collaboration'|'support'|'other', 'confidence': 0.85}
```

**3) Генерация ответа (Response Generation)**
```python
ai_response = ai_service.generate_response(name, comment)
# "Спасибо за обращение, мы свяжемся с вами в ближайшее время."
```

### Промпты

Анализ тональности и классификация:
```
Analyze the sentiment of the following comment and respond in JSON format:
Comment: {text}

Response should be JSON with keys: sentiment (positive/negative/neutral), score (0-1), reasoning (brief explanation)
```

Генерация ответа:
```
Generate a professional and friendly response to the following customer inquiry:
Customer Name: {name}
Comment: {text}

The response should be warm, professional, and address their concern. Keep it to 2-3 sentences.
```

### Graceful Fallback

Если OpenAI недоступен или ключ не указан:

```python
def analyze_sentiment(text: str) -> dict:
    if not self.api_key:
        logger.warning("OpenAI API key not configured")
        return self._fallback_sentiment_analysis(text)

    try:
        # вызов OpenAI API
        ...
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        return self._fallback_sentiment_analysis(text)

def _fallback_sentiment_analysis(self, text: str) -> dict:
    # Простой анализ на основе ключевых слов
    positive_words = ['good', 'great', 'excellent', 'awesome', ...]
    negative_words = ['bad', 'terrible', 'awful', 'hate', ...]

    text_lower = text.lower()
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)

    if pos_count > neg_count:
        return {'sentiment': 'positive', 'score': 0.8, 'reasoning': 'Fallback analysis'}
    elif neg_count > pos_count:
        return {'sentiment': 'negative', 'score': 0.2, 'reasoning': 'Fallback analysis'}
    else:
        return {'sentiment': 'neutral', 'score': 0.5, 'reasoning': 'Fallback analysis'}
```

Преимущества:
- ✅ API всегда доступен, даже без OpenAI ключа
- ✅ Сервис работает, пока есть интернет-соединение для остальных операций
- ✅ Все ошибки AI логируются в `logs/errors.log`

Тест fallback: оставьте `OPENAI_API_KEY` пустым в `.env`, отправьте `POST /api/contact/` — в ответе будет `sentiment: "neutral"` и дефолтный `ai_reply`, статус всё равно `201 Created`.

---

## 6. Что сделано с помощью AI

### Части кода, сгенерированные AI (ChatGPT/Copilot)

| Файл | % сгенерировано | Промпт | Что доработано вручную |
|------|------------------|--------|--------------------------|
| `api/services/ai_service.py` | 70% | "Write a service class for OpenAI sentiment analysis with graceful fallback" | Добавлены fallback-эвристики, обработка исключений, логирование |
| `api/services/email_service.py` | 80% | "Generate email service for Django with admin and user confirmation emails" | Адаптирован под модель контакта, добавлены шаблоны писем |
| `api/repositories/contact_repository.py` | 90% | "Create repository pattern for Django ORM ContactSubmission model" | Минимальные правки |
| `api/serializers/contact_serializer.py` | 80% | "Write DRF serializer for contact form with email and phone validation" | Усилена валидация (регулярные выражения) |

### Архитектурные решения (сделаны вручную)

- Слоистая архитектура — разделение на Views → Services → Repositories
- Graceful fallback для AI — логика обработки ошибок
- Rate limiting — файловое хранилище + логирование
- Exception handler — кастомная обработка ошибок API
- Middleware — перехват запросов для логирования

### Промпты, которые использовались

```
1. "Create a service class for OpenAI API that analyzes sentiment and generates responses
    with graceful fallback if API fails."

2. "Write a DRF serializer for contact form with validation for name, email, phone, comment."

3. "Generate email service for Django that sends confirmation to admin and user."

4. "Create repository pattern class for Django ORM ContactSubmission model."
```

---

## 7. Хранение данных

### Модели (SQLite)

```python
class ContactSubmission(models.Model):
    id = UUIDField(primary_key=True)
    name = CharField(max_length=100)
    phone = CharField(max_length=20)
    email = EmailField()
    comment = TextField()
    sentiment = CharField(choices=[...])        # positive/neutral/negative
    ai_response = TextField()                   # Ответ от AI
    request_type = CharField(choices=[...])     # inquiry/feedback/collaboration/...
    created_at = DateTimeField(auto_now_add=True)
    ip_address = GenericIPAddressField()
```

Файл БД: `db.sqlite3` (создаётся после `migrate`).

### Логирование

Файлы:
- `logs/api.log` — все запросы и события
- `logs/errors.log` — только ошибки (level=ERROR)

Формат:
```
INFO  2024-07-17 15:30:45,123 contact_view REQUEST POST /api/contact/ from 127.0.0.1
INFO  2024-07-17 15:30:46,456 ai_service AI Sentiment Analysis: {'sentiment': 'positive', 'score': 0.85}
INFO  2024-07-17 15:30:47,789 email_service Confirmation email sent to ivan@example.com
INFO  2024-07-17 15:30:48,012 metrics_service Metrics recorded for submission
ERROR 2024-07-17 15:30:50,345 ai_service OpenAI error: RateLimitError
```

Настройка в `settings.py`:
```python
LOGGING = {
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/api.log',
            'level': 'INFO',
        },
        'error_file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/errors.log',
            'level': 'ERROR',
        },
    },
    'loggers': {
        'api': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
        },
    },
}
```

### Rate Limiting

Реализовано через **DRF Throttling + файловое хранилище**.

Хранилище: `data/rate_limit.json`

```json
{
  "127.0.0.1": ["2024-07-17T15:30:45.123", "2024-07-17T15:30:46.456"],
  "192.168.1.100": [...]
}
```

Логика:
1. Для каждого IP сохраняются timestamps последних запросов
2. При новом запросе проверяется количество запросов за последние `RATE_LIMIT_MINUTES`
3. Если превышено `RATE_LIMIT_REQUESTS` — возвращается `HTTP 429`
4. Старые timestamps удаляются из файла

Конфигурация в `.env`:
```env
RATE_LIMIT_REQUESTS=5      # максимум запросов
RATE_LIMIT_MINUTES=10      # за этот период в минутах
```

### Метрики

Хранилище: `data/metrics.json`

```json
{
  "total_submissions": 42,
  "by_sentiment": { "positive": 15, "neutral": 20, "negative": 7 },
  "by_type": { "inquiry": 10, "feedback": 15, "collaboration": 12, "support": 5 },
  "last_updated": "2024-07-17T15:30:00.000Z"
}
```

Обновляется после каждого успешного создания контакта; метрики разбиты по `sentiment` и `request_type` для аналитики.

---

## 8. Примеры запросов (Postman / curl)

### Способ 1: Импорт Postman-коллекции

1. Откройте **Postman → File → Import**
2. Выберите файл `Postman_Collection.json` из проекта
3. Коллекция «Developer Landing API» содержит 7 готовых запросов

### Способ 2: curl (PowerShell)

**Успешная отправка формы**
```powershell
$body = @{
    name = "Иван Петров"
    phone = "+71234567890"
    email = "ivan@example.com"
    comment = "Здравствуйте! Хочу обсудить сотрудничество по вашему проекту."
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/contact/" `
                  -Method POST `
                  -Headers @{"Content-Type"="application/json"} `
                  -Body $body
```

**Health check**
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/health/" -Method GET
```

**Метрики**
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/metrics/" -Method GET
```

**Ошибка валидации**
```powershell
$body = @{
    name = "Test"
    phone = "123"
    email = "invalid-email"
    comment = "Коротко"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/contact/" `
                  -Method POST `
                  -Headers @{"Content-Type"="application/json"} `
                  -Body $body
```
Ожидаемый ответ (`400`):
```json
{
  "name": ["Ensure this field has at least 2 characters."],
  "phone": ["Номер телефона должен содержать 9-15 цифр"],
  "email": ["Enter a valid email address."],
  "comment": ["Ensure this field has at least 10 characters."]
}
```

### Тест Rate Limiting (429)

Отправьте 6 POST-запросов подряд (лимит по умолчанию — 5 запросов за 10 минут):

```powershell
for ($i = 1; $i -le 6; $i++) {
    Write-Host "Запрос #$i"
    $body = @{
        name = "Test User"
        phone = "+71234567890"
        email = "test@example.com"
        comment = "Test comment for rate limiting"
    } | ConvertTo-Json

    try {
        $response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/contact/" `
                                      -Method POST `
                                      -Headers @{"Content-Type"="application/json"} `
                                      -Body $body
        Write-Host "Status: 201, Message: $($response.message)"
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.Value__
        Write-Host "Status: $statusCode, Error: Too many requests"
    }
    Start-Sleep -Milliseconds 100
}
```

На 6-м запросе ожидается `429 Too Many Requests`.

### Примеры разных тональностей и типов запросов

| Комментарий | Ожидаемый sentiment | Ожидаемый request_type |
|-------------|---------------------|--------------------------|
| «Отличная работа! Просто превосходно! Все очень хорошо, спасибо вам!» | positive | feedback |
| «Хочу узнать информацию о вашем проекте и услугах. Возможно сотрудничество.» | neutral | inquiry |
| «Плохо, ужасно, кошмар! Ничего не работает, очень недоволен.» | negative | support |
| «Хочу предложить наше сотрудничество. Давайте обсудим партнерство.» | positive | collaboration |

### Просмотр Swagger документации

Откройте в браузере: `http://127.0.0.1:8000/api/docs/` — интерактивная Swagger UI, эндпоинты можно тестировать прямо оттуда.

### Проверка хранилища данных

```powershell
# Логи
Get-Content .\logs\api.log
Get-Content .\logs\errors.log
Get-Content .\logs\api.log -Tail 20 -Wait

# Метрики
Get-Content .\data\metrics.json | ConvertFrom-Json | ConvertTo-Json -Depth 3

# Rate limit
Get-Content .\data\rate_limit.json | ConvertFrom-Json

# Количество контактов в БД
python manage.py shell
>>> from api.models import ContactSubmission
>>> ContactSubmission.objects.count()
```

---

## 9. Решение проблем (Troubleshooting)

**"Python не найден"**
```powershell
python --version
# если не работает:
py --version
```

**venv не активируется**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\.venv\Scripts\Activate.ps1
```

**Зависимости не установились**
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

**Ошибка миграций**
```powershell
rm .\db.sqlite3
rm -r .\logs
rm -r .\data
python manage.py makemigrations
python manage.py migrate
```

**Порт 8000 занят**
```powershell
python manage.py runserver 8001
```

**Ошибка OpenAI** — это нормально: сервис использует fallback-механизм. Если `OPENAI_API_KEY` в `.env` пуст, будет использована эвристика, ошибка запишется в `logs/errors.log`, а API всё равно вернёт `201 Created`.

---



**Версия API:** 1.0.0

# PayFlow

**Платформа обработки платежей на микросервисной архитектуре**

Событийно-ориентированная система из двух микросервисов на Python, связанных через Apache Kafka. Моделирует реальный финтех-сценарий: приём платежа, взаимодействие с внешним провайдером, публикация событий и их обработка для аналитики.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-async-009688)
![Kafka](https://img.shields.io/badge/Apache%20Kafka-aiokafka-black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-SQLAlchemy%202.0-336791)
![Redis](https://img.shields.io/badge/Redis-redis--py-DC382D)
![Docker](https://img.shields.io/badge/Docker-compose-2496ED)

---

## 📖 О проекте

**PayFlow** — упрощённая платформа обработки платежей, состоящая из двух микросервисов, связанных через Apache Kafka. Проект воспроизводит сценарий, типичный для финтех-компаний (Тинькофф, Сбер, Яндекс Pay, Ozon Fintech): приём платежа → взаимодействие с внешним платёжным провайдером → публикация события → обработка события для аналитики.

Паттерны, реализуемые в проекте, регулярно встречаются на собеседованиях на позицию **Middle / Middle+ Python Backend**.

### Почему микросервисы, а не монолит

Монолит хорош до определённого масштаба. Когда над продуктом работают несколько команд, нужна независимая деплой-поставка, а отказ одного компонента не должен ронять всю систему — микросервисы становятся обоснованным выбором. В финтехе это критично: сервис приёма платежей должен работать, даже если сервис аналитики лежит.

### Почему Kafka, а не RabbitMQ или HTTP

Kafka — стандарт межсервисного взаимодействия в российском финтехе. В отличие от синхронных HTTP-вызовов, она даёт:

- **Асинхронность** — producer не ждёт consumer;
- **Гарантии доставки** — at-least-once;
- **Сохранение истории** событий;
- **Горизонтальное масштабирование** через consumer groups.

RabbitMQ тоже используется, но для high-throughput сценариев Kafka — доминирующий выбор.

---

## 🏗 Архитектура

┌──────────┐ ┌───────────────────┐ ┌────────────────────────────┐
│ Клиент │─────▶│ Payment Service │─────▶│ Kafka │
└──────────┘ │ (producer) │ │ topic: payment.events │
│ FastAPI + PG │ └────────────┬───────────────┘
│ + Outbox │ │
└───────────────────┘ ▼
┌────────────────────────────┐
│ Transaction Analytics │
│ Service (consumer) │
│ FastAPI + Redis │
└────────────────────────────┘


### Payment Service (producer)

Принимает запросы на создание платежа, взаимодействует с внешним платёжным провайдером (мок), сохраняет результат в PostgreSQL и публикует событие в Kafka через **Outbox-таблицу**.

### Transaction Analytics Service (consumer)

Потребляет события из Kafka, агрегирует данные по транзакциям и предоставляет API для аналитики. Использует Redis для кеширования и защищён от повторной обработки событий (**идемпотентный consumer**).

---

## 🛠 Технологический стек

| Категория | Технология | Зачем |
|---|---|---|
| Язык | Python 3.11+ | Async / await |
| Фреймворк | FastAPI | REST API, async, автодокументация |
| БД | PostgreSQL + SQLAlchemy 2.0 (async) | Основное хранилище |
| Миграции | Alembic | Версионирование схемы БД |
| Брокер | Apache Kafka (aiokafka) | Межсервисные события |
| Кеш | Redis (redis-py) | Кеширование, идемпотентность |
| Валидация | Pydantic v2 | Схемы, настройки, DTO |
| Контейнеризация | Docker + docker-compose | Локальный запуск всего стека |
| Тесты | pytest + httpx + testcontainers | Юнит- и интеграционные тесты |
| Логирование | structlog | Структурированные JSON-логи |

---

## 🎯 Паттерны

| Паттерн | Зачем | Где |
|---|---|---|
| **Outbox Pattern** | Атомарность: сохранение в БД и отправка события в Kafka происходят вместе или не происходят вовсе | Payment Service |
| **Retry** | Повтор запроса при временном сбое внешнего сервиса (exponential backoff) | Payment Service |
| **Circuit Breaker** | Прекращает обращения к упавшему сервису, даёт время восстановиться | Payment Service |
| **Idempotent Consumer** | Защита от повторной обработки события (at-least-once delivery) | Analytics Service |
| **Health Check** | Liveness/readiness-пробы для оркестратора (K8s / docker-compose) | Оба сервиса |
| **Graceful Shutdown** | Корректное завершение consumer без потери событий | Analytics Service |

---

## 📂 Структура репозитория

Монорепозиторий (для учебного проекта удобнее отдельных репозиториев):

payflow/
├── docker-compose.yml
├── payment-service/
│ ├── app/
│ │ ├── api/ # роутеры FastAPI
│ │ ├── core/ # конфиг, логирование
│ │ ├── models/ # SQLAlchemy-модели
│ │ ├── schemas/ # Pydantic-схемы
│ │ ├── services/ # бизнес-логика
│ │ ├── integrations/ # внешние сервисы, Kafka producer
│ │ └── main.py
│ ├── alembic/
│ ├── tests/
│ ├── Dockerfile
│ └── pyproject.toml
├── analytics-service/
│ ├── app/ # аналогичная структура + consumer/
│ ├── tests/
│ ├── Dockerfile
│ └── pyproject.toml
└── README.md


---

## 🚀 Быстрый старт

```bash
git clone https://github.com/<your-username>/payflow.git
cd payflow
cp .env.example .env
docker-compose up --build


---

## 🚀 Быстрый старт

```bash
git clone https://github.com/<your-username>/payflow.git
cd payflow
cp .env.example .env
docker-compose up --build

Payment Service — http://localhost:8001/docs

Analytics Service — http://localhost:8002/docs

Kafka UI — http://localhost:8080 (если включён в compose)
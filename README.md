# Product Importer

A Django-based product import application with Django REST Framework, Celery for async tasks, PostgreSQL database, and Redis for caching/broker.

## Tech Stack

- Python 3.11+
- Django 5.x
- Django REST Framework
- PostgreSQL
- Celery with Redis
- Docker & Docker Compose

## Quick Start

1. **Copy environment variables**
   ```bash
   cp .env.example .env
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

This will start:
- Django web server at http://localhost:8000
- PostgreSQL database on port 5432
- Redis on port 6379
- Celery worker
- Celery beat scheduler

## Django Admin

1. Create a superuser:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

2. Access Django Admin at http://localhost:8000/admin/

## Development Commands

- **Run migrations**: `docker-compose exec web python manage.py migrate`
- **Create superuser**: `docker-compose exec web python manage.py createsuperuser`
- **Collect static files**: `docker-compose exec web python manage.py collectstatic`
- **Shell access**: `docker-compose exec web python manage.py shell`

## Project Structure

```
.
├── config/          # Django project configuration
├── products/        # Products app
├── docker-compose.yml
├── Dockerfile       # Web server Dockerfile
├── Dockerfile.celery # Celery Dockerfile
└── requirements.txt
```

## Environment Variables

See `.env.example` for all available environment variables.
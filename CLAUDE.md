# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

**Start development server:**
```bash
python manage.py runserver
```

**Run tests:**
```bash
python manage.py test
```

**Run linting:**
```bash
pylint homepage website
```

**Database migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

**Collect static files:**
```bash
python manage.py collectstatic
```

**Run in Docker:**
```bash
docker build -t personal-website .
docker run -p 8000:8000 personal-website
```

## Architecture Overview

This is a Django personal website with the following structure:

- **Main Django project:** `website/` - Contains settings, main URL configuration
- **Homepage app:** `homepage/` - Single Django app handling all page views
- **Templates:** `templates/` - HTML templates using Bootstrap 5
- **Static files:** Served via Django's static file handling

### Key Components

**Settings (`website/settings.py`):**
- Supports both SQLite (local) and PostgreSQL (production) databases
- OpenTelemetry instrumentation for monitoring with OTLP exports
- Environment-based configuration for secrets and deployment modes
- Custom logging configuration with file rotation and OTLP export

**Views (`homepage/views.py`):**
- Simple template-based views for static pages (home, resume, projects, contact)
- Health check endpoint at `/_health/` for monitoring
- OCI webhook endpoint for Discord notifications

**Database:**
- Uses SQLite for local development (when `secret_key` file exists)
- PostgreSQL for production (configured via environment variables)
- No custom models - uses Django defaults

### Development Environment

**Local development indicators:**
- Presence of `secret_key` file enables DEBUG mode and SQLite
- ALLOWED_HOSTS includes 'localhost' when in debug mode
- Simplified logging (console only) in debug mode

**Production deployment:**
- Uses Docker with Python 3.13 slim image
- Installs custom OpenTelemetry packages from forks to fix upstream bugs
- Gunicorn for WSGI serving (configured in requirements.txt)

### OpenTelemetry Integration

The application has comprehensive observability:
- Tracing via OpenTelemetry Django instrumentation
- Custom logging handler (`otlp.py`) for log export
- OTLP exporters for both traces and logs
- Instrumentation is skipped during test runs
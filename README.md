# Response-Connect

A Flask application scaffold that uses blueprints, SQLAlchemy, and Docker Compose with PostgreSQL.

## Quick start

1. Copy the example environment file:
   `cp .env.example .env`
2. Start the stack:
   `docker compose up --build`
3. Open the app at:
   `http://localhost:8000/`

## Application structure

- `app/` contains the Flask application factory, configuration, extensions, and blueprint packages.
- `app/blueprints/auth/` contains authentication and permission endpoints plus their blueprint-owned model definitions.
- `app/blueprints/personal/` contains individual staff workflows such as shift requests and HR-related routes.
- `app/blueprints/org/` contains organisation and admin functions.
- `app/blueprints/api/` contains public/internal API endpoints and API client models.
- `app/blueprints/job_application/` contains recruitment and external applicant workflows.
- `app/blueprints/external/` contains external-facing forms such as patient evaluation and complaints.
- `app/blueprints/main/__init__.py` exposes the default route and validates the database connection.
- `wsgi.py` provides the production WSGI entry point used by Gunicorn.

## Included files

- `Dockerfile` builds the Flask application container.
- `docker-compose.yml` runs the Flask app and PostgreSQL service together.
- `app.py` remains a lightweight compatibility entry point to the factory.
- `.env.example` contains the default PostgreSQL settings.


# Response-Connect

A Flask application scaffold that uses blueprints, SQLAlchemy, and Docker Compose with PostgreSQL.

## Quick start

1. Copy the example environment file:
   `cp .env.example .env`
2. Start the production stack:
   `docker compose up --build`
3. Open the app at:
   `http://localhost:8000/`

For local development with live reloading, use the development override file:
`docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build`

The development override bind-mounts the repository into the web container and starts Flask in debug mode, so changes to Python, templates, and static assets are reloaded automatically.

## Migration workflow

This project uses Alembic for database schema versioning.

The Alembic environment loads the same `.env` values as the Flask app, so the database connection is driven by the same secrets and configuration. Do not hardcode credentials in the repo.

Apply the latest schema:
`alembic upgrade head`

Create a new migration after changing a model:
`alembic revision --autogenerate -m "describe your change"`

## Initial admin bootstrap

Create the first administrator account from the command line:

`docker compose exec web flask create-admin --email admin@example.com --password ChangeMe123! --first-name System --last-name Administrator`

This command seeds the hardwired permission catalog, creates the default `admin` and `staff` roles, and assigns the admin role to the initial user.

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


# Response Connect

Response Connect is an open-source operational management platform for ambulance services, healthcare providers, emergency-response organisations and other public-safety teams.

It is being designed to bring workforce administration, operational control, compliance, files, incidents, patient transport, fleet, equipment and organisational governance into one coherent system.

The project is built around a simple principle:

> Build capabilities once. Reuse them everywhere.

Rather than implementing each function as an isolated module, Response Connect provides shared platform capabilities for files, catalogues, reference data, permissions, lifecycle management, operational events and audit history.

## Project status

Response Connect is under active development and is not yet ready for production use.

The current development phase is:

```text
Platform Foundation and Consolidation
```

Implemented foundations currently include:

* Flask application and modular blueprint structure;
* PostgreSQL persistence and Alembic migrations;
* Docker-based deployment;
* Redis, Celery worker and Celery Beat services;
* S3-compatible file storage using MinIO;
* immutable managed file records;
* Flask-streamed file downloads;
* authentication, roles and permissions;
* organisation and personal application areas;
* catalogue framework primitives;
* file-processing policies;
* reference-data registration and synchronisation;
* structured platform logging;
* architecture handbook and delivery roadmap.

Major foundational capabilities still planned include:

* Event Journal;
* operational and audit logs;
* lifecycle and assignment behaviour;
* Desk hierarchy and Desk-scoped access;
* File Types and file-processing pipelines;
* notifications;
* search;
* reporting.

The active implementation roadmap is maintained in [docs/ROADMAP.md](docs/ROADMAP.md).

## What Response Connect is intended to support

Response Connect is being designed to support several connected operational domains.

### Workforce and compliance

Planned capabilities include:

* staff records;
* job positions;
* clinical grades;
* qualifications;
* competencies;
* mandatory training;
* evidence and certificates;
* professional registrations;
* expiry and renewal;
* deployment compliance.

### Operational control

Operational work will be organised through hierarchical **Desks**.

A Desk represents an operational workspace or control boundary, rather than necessarily a physical desk or location.

Examples include:

```text
Company Operations
├── Event Medical
│   ├── Glastonbury Festival 2026
│   └── Exeter Christmas Market
├── Patient Transport
│   ├── Devon
│   ├── Cornwall
│   └── Somerset
└── Ambulance Operations
    ├── North Area
    └── South Area
```

A Desk may provide access to:

* CAD and dispatch functions;
* incidents;
* patient journeys;
* resources;
* vehicles;
* staff sign-in;
* tasks;
* communications;
* dashboards;
* an operational log.

### Events and audit history

A shared Event Journal is planned to underpin:

* company-wide operational logs;
* Desk logs;
* event and incident timelines;
* shift logs;
* resource histories;
* administrative audit records;
* security events;
* system-processing events.

The Event Journal will not replace normal domain models. Domain tables will remain the source of current state, while the journal preserves immutable history.

### Files and documents

The Files platform is designed to provide:

* S3-compatible storage;
* immutable file objects;
* generated object keys;
* SHA-256 integrity hashes;
* upload validation;
* streamed downloads;
* soft deletion;
* restoration;
* permanent purge;
* file-processing policies;
* future malware scanning;
* previews and thumbnails;
* document versioning;
* evidence attachments.

Business modules will use the Files platform rather than accessing S3 or MinIO directly.

### Operational resources

Future operational modules are expected to manage:

* people;
* vehicles;
* medical teams;
* equipment;
* treatment centres;
* radios;
* specialist response units.

The underlying domain records will remain separate, while shared operational views may expose common properties such as availability, location, status, capabilities and current Desk.

### Governance and organisational knowledge

Planned governance capabilities include:

* controlled policies and procedures;
* document review and approval;
* version history;
* acknowledgements;
* internal audits;
* risks;
* findings;
* actions;
* complaints and incidents;
* evidence;
* governance reporting.

## Architecture

Response Connect is designed in layers:

```text
Business and operational modules
                ↓
Shared organisational domains
                ↓
Platform capabilities
                ↓
Infrastructure providers
```

Dependencies should generally flow downwards.

Platform capabilities must not depend on business-specific modules.

### Platform capabilities

The principal platform capabilities are intended to include:

* authentication;
* permissions and authorisation;
* catalogues;
* reference data;
* files and content;
* platform logging;
* Event Journal;
* lifecycle;
* notifications;
* search;
* reporting.

### Shared organisational domains

Shared domains include:

* Organisation;
* People;
* Locations;
* Desks;
* Vehicles;
* Equipment;
* Resources.

### Business modules

Business modules compose platform and shared-domain services.

Examples include:

* Workforce;
* Competencies;
* Event Medical;
* Patient Transport;
* Incidents and CAD;
* Fleet;
* Equipment and Stock;
* Library and Governance.

## Core architectural principles

Response Connect follows several project-wide rules.

### Platform before product

Reusable capabilities should be built once at platform level rather than recreated within individual modules.

### Single ownership

Every concept has one owning module.

Other modules may reference that concept through its public services, but they do not redefine its lifecycle or business rules.

### Service-layer workflows

Routes handle HTTP concerns.

Services own:

* business workflows;
* validation;
* transactions;
* lifecycle transitions;
* event creation;
* calls to other platform capabilities.

### Stable machine identifiers

Application logic uses stable codes rather than editable display names.

Examples include:

```text
files:upload
pdf_document
mandatory_training
vehicle.arrived_on_scene
```

### Immutable history

Stored file content, audit history, event history and document versions should be extended rather than silently rewritten.

### Self-hosting first

The platform must remain practical to deploy using Docker on infrastructure controlled by the installation owner.

External cloud services may be supported, but must not become mandatory.

### Progressive enhancement

The application is server-rendered.

HTMX enhances normal HTML workflows rather than replacing the server with a separate client application.

## Technology stack

The current stack includes:

* Python;
* Flask;
* Flask-SQLAlchemy;
* PostgreSQL;
* Alembic and Flask-Migrate;
* HTMX;
* Jinja templates;
* Redis;
* Celery;
* MinIO or another S3-compatible object store;
* Gunicorn;
* Docker Compose;
* Iconify using Tabler icons;
* Pytest.

## Deployment model

Response Connect currently assumes:

* one organisation per installation;
* one independent database per installation;
* one independent object-storage configuration per installation;
* no shared multi-tenant application database.

An organisation may self-host the application or operate it within a dedicated hosted virtual machine.

This model is intended to reduce:

* data-isolation risk;
* cross-tenant leakage;
* operational complexity;
* difficult tenant-specific migrations.

## Docker services

The standard Compose deployment currently includes:

| Service  | Purpose                                   |
| -------- | ----------------------------------------- |
| `web`    | Flask application served through Gunicorn |
| `worker` | Celery background-task worker             |
| `beat`   | Celery scheduled-task service             |
| `db`     | PostgreSQL database                       |
| `redis`  | Celery broker and result backend          |
| `minio`  | S3-compatible object storage              |

The web application is exposed on:

```text
http://localhost:8000
```

The local MinIO administration console is exposed on:

```text
http://localhost:9001
```

The MinIO console is bound to the local machine by default.

## Quick start

### 1. Clone the repository

```bash
git clone https://github.com/Ambulant-Solutions/Response-Connect.git
cd Response-Connect
```

### 2. Create the environment file

```bash
cp .env.example .env
```

Review `.env` before starting the application.

At minimum, replace:

```text
SECRET_KEY
POSTGRES_PASSWORD
S3_SECRET_KEY
```

with strong random values.

Email settings may remain unconfigured until outgoing mail is required.

### 3. Build and start the containers

```bash
docker compose up -d --build
```

Check the services:

```bash
docker compose ps
```

### 4. Apply database migrations

```bash
docker compose exec web flask db upgrade
```

### 5. Initialise object storage

```bash
docker compose exec web flask files-init
```

This ensures the configured S3 bucket exists.

### 6. Synchronise system reference data

List the registered datasets:

```bash
docker compose exec web flask reference-data list
```

Preview changes:

```bash
docker compose exec web flask reference-data sync --dry-run
```

Apply the definitions:

```bash
docker compose exec web flask reference-data sync
```

Reference-data synchronisation is designed to be idempotent.

It creates missing system records and updates system-owned fields while preserving locally owned display customisations.

### 7. Create the initial administrator

```bash
docker compose exec web flask create-admin \
  --email admin@example.com \
  --password 'replace-with-a-strong-password' \
  --first-name System \
  --last-name Administrator
```

### 8. Open the application

```text
http://localhost:8000
```

## Development mode

A development override is available for local work:

```bash
docker compose \
  -f docker-compose.yml \
  -f docker-compose.dev.yml \
  up -d --build
```

The development configuration bind-mounts the source repository and enables automatic reload behaviour.

Container logs can be viewed with:

```bash
docker compose logs -f web
```

Worker logs:

```bash
docker compose logs -f worker
```

Scheduled-task logs:

```bash
docker compose logs -f beat
```

## Database migrations

Response Connect uses Flask-Migrate and Alembic.

After changing SQLAlchemy models, generate a migration:

```bash
docker compose exec web flask db migrate \
  -m "Describe the schema change"
```

Inspect the generated migration carefully before applying it.

Apply the migration:

```bash
docker compose exec web flask db upgrade
```

Show the current revision:

```bash
docker compose exec web flask db current
```

Migration files must be committed to the repository.

Reference data and database migrations serve different purposes:

* migrations change database structure or transform stored data;
* reference-data synchronisation manages system-provided records identified by stable codes.

## Testing

Run the complete test suite with:

```bash
docker compose exec web python -m pytest
```

Run a specific directory:

```bash
docker compose exec web python -m pytest tests/files
```

Run one test file:

```bash
docker compose exec web python -m pytest \
  tests/test_job_position_routes.py
```

Use `python -m pytest` rather than invoking the `pytest` executable directly so the tests use the same interpreter and import path as the application.

The current test coverage includes:

* file-management workflows;
* file-processing policies;
* catalogue validators;
* reference-data behaviour;
* structured platform logging;
* organisation settings routes;
* workforce settings such as Job Positions.

A dedicated PostgreSQL test database and wider integration testing remain on the roadmap.

## Reference-data commands

List registered datasets:

```bash
docker compose exec web flask reference-data list
```

Synchronise all datasets:

```bash
docker compose exec web flask reference-data sync
```

Synchronise one dataset:

```bash
docker compose exec web flask reference-data sync \
  --dataset files.processing_policies
```

Preview one dataset:

```bash
docker compose exec web flask reference-data sync \
  --dataset files.processing_policies \
  --dry-run
```

Current file-processing policies include:

```text
generic_binary
pdf_document
standard_image
profile_photo
archive
```

## File storage

Local deployments use MinIO as the S3-compatible provider.

The architecture permits a compatible external S3 service to be configured later without changing business modules.

Managed uploads use:

* generated object keys;
* immutable binary objects;
* SHA-256 hashes;
* persisted file metadata;
* service-controlled upload and download workflows.

Downloads are streamed through Flask rather than exposing object-storage URLs directly.

This simplifies deployment and keeps application authorisation in control of every download.

## Application structure

The current repository structure includes:

```text
app/
├── blueprints/
│   ├── api/
│   ├── auth/
│   ├── external/
│   ├── job_application/
│   ├── jobs/
│   ├── main/
│   ├── org/
│   └── personal/
├── catalogues/
├── files/
├── reference_data/
├── templates/
├── static/
├── config.py
├── extensions.py
└── platform_logging.py

docs/
├── architecture/
└── ROADMAP.md

migrations/
tests/
docker-compose.yml
docker-compose.dev.yml
Dockerfile
wsgi.py
```

### `app/blueprints/`

Contains the current user-facing application areas and business routes.

### `app/catalogues/`

Contains shared catalogue primitives, validation, exceptions and base service behaviour.

### `app/files/`

Contains the S3 provider, file manager, immutable file models, processing policies, commands and reference-data integration.

### `app/reference_data/`

Contains reference-data definitions, registry behaviour, synchronisation contracts and CLI support.

### `docs/architecture/`

Contains the architectural handbook and shared project conventions.

### `docs/ROADMAP.md`

Contains the consolidated, ordered delivery plan.

It should be reviewed and updated before significant work begins.

## Current user-facing areas

The application currently contains foundations for:

* authentication;
* personal staff views;
* organisation administration;
* organisation settings;
* people records;
* locations and location types;
* roles and permissions;
* workforce settings;
* Job Positions;
* Mandatory Training Course definitions;
* recruitment and job applications;
* external-facing forms;
* file management.

Some areas are structural placeholders for planned functionality and are not yet complete.

## Planned operational architecture

The next major foundation will be the Event Journal.

It will provide one immutable event store that can support:

* operational activity;
* administrative audit history;
* system events;
* security events;
* Desk timelines;
* record timelines.

Following the Event Journal, the planned order is:

1. lifecycle behaviour;
2. Desk hierarchy and access;
3. Operational Log and Audit Log projections;
4. File Types and upload-policy integration;
5. Clinical Grades;
6. competencies and mandatory training;
7. operational modules such as Event Control, Patient Transport and CAD.

The authoritative order is maintained in [docs/ROADMAP.md](docs/ROADMAP.md).

## Architecture documentation

Start with:

* [Architecture Guide](docs/architecture/README.md)
* [Platform Principles](docs/architecture/01-platform-principles.md)
* [Project Structure and Module Boundaries](docs/architecture/02-project-structure.md)
* [Module Conventions](docs/architecture/03-module-conventions.md)
* [Service-Layer Conventions](docs/architecture/04-service-layer-conventions.md)
* [Core Concepts and Shared Vocabulary](docs/architecture/05-core-concepts.md)
* [Catalogue Framework](docs/architecture/06-catalogue-framework.md)
* [Platform Overview and Operational Architecture](docs/architecture/07-platform-overview.md)
* [Delivery Roadmap](docs/ROADMAP.md)

## Contribution expectations

Response Connect is intended to become a contributor-friendly open-source project.

Until the dedicated contribution guide is completed, changes should follow these principles:

1. Review `docs/ROADMAP.md` before beginning work.
2. Read the relevant architecture chapter.
3. Preserve module ownership.
4. Place business workflows in services.
5. Use stable codes for application-controlled identities.
6. Use public module interfaces.
7. Add or update tests.
8. Generate and inspect migrations.
9. Update documentation.
10. Update the roadmap when work changes project status or priorities.

Do not introduce a second implementation of an existing platform capability merely to avoid extending the current one.

## Security and production readiness

The repository is currently an active development project.

Before production use, the project still requires additional work including:

* security review;
* production configuration guidance;
* isolated test infrastructure;
* CI;
* backup and restore testing;
* event and audit persistence;
* malware scanning;
* retention controls;
* health checks and monitoring;
* deployment hardening;
* upgrade testing;
* user and administrator documentation.

Do not treat the current `main` branch as a supported production release.

## Licence

The project’s open-source licence should be recorded here once the final licence file has been selected and committed.

Until then, the presence of source code in a public repository should not be treated as a complete licence grant.

## Maintainers

Response Connect is currently developed by Ambulant Solutions as an open-source operational management platform.

Project governance, contribution rules, release processes and support arrangements will be documented as the project matures.

# Project Structure and Module Boundaries

## Purpose

This document defines the expected structure of the Response Connect codebase and the boundaries between platform capabilities, shared domain modules and business modules.

The structure is intended to make the project:

* predictable to navigate;
* easier to test;
* safer to extend;
* suitable for external contributors;
* resistant to duplicated implementation patterns.

The exact file layout may evolve, but module ownership and service boundaries should remain clear.

# Application layers

Response Connect is organised into four conceptual layers.

## Infrastructure

Infrastructure provides technical services used by the application.

Examples include:

* PostgreSQL;
* Redis;
* Celery;
* S3-compatible object storage;
* Flask;
* SQLAlchemy;
* outbound email transports.

Business modules must not access infrastructure clients directly.

Infrastructure integrations should be wrapped by platform services.

## Platform capabilities

Platform capabilities provide reusable application-wide functionality.

Examples include:

* authentication;
* permissions;
* catalogues;
* files;
* audit;
* reference data;
* notifications;
* workflows;
* search;
* reporting.

These capabilities should expose stable service interfaces that other modules can use.

## Shared domain modules

Shared domain modules represent concepts used across several operational areas.

Examples include:

* people;
* organisations;
* locations;
* competencies;
* tasks;
* assets;
* vehicles;
* equipment;
* library records.

Shared domain modules may use platform capabilities but should not bypass their public interfaces.

## Business modules

Business modules implement operational workflows for particular use cases.

Examples include:

* ambulance operations;
* event medical cover;
* patient transport;
* incidents;
* dispatch;
* clinical activity;
* shift management;
* recruitment;
* fleet operations.

Business modules should remain focused on domain behaviour and should reuse platform and shared domain capabilities.

# Current repository structure

The current Flask application uses the following broad structure:

```text
app/
├── __init__.py
├── config.py
├── extensions.py
├── blueprints/
│   ├── auth/
│   ├── main/
│   ├── org/
│   ├── personal/
│   ├── people/
│   └── ...
├── files/
│   ├── __init__.py
│   ├── exceptions.py
│   ├── http.py
│   ├── keys.py
│   ├── manager.py
│   ├── models.py
│   └── providers/
│       ├── __init__.py
│       └── s3.py
├── templates/
└── static/
```

The project may gradually move shared capabilities outside `blueprints` where they are not primarily HTTP-facing.

A package does not need to be a Flask blueprint merely because it contains application logic.

# Recommended module structure

A mature module should normally use the following shape:

```text
module_name/
├── __init__.py
├── blueprint.py
├── models.py
├── routes.py
├── services.py
├── forms.py
├── validators.py
├── exceptions.py
├── permissions.py
├── seeds.py
├── tasks.py
├── templates/
│   └── module_name/
├── static/
│   └── module_name/
└── tests/
```

Not every module requires every file.

Files should only be created when their responsibility exists. Empty placeholder modules should be avoided.

# File responsibilities

## `__init__.py`

The package initializer should expose the module's supported public interface.

It should avoid:

* complex business logic;
* database writes;
* expensive startup operations;
* circular import workarounds that hide unclear boundaries.

Example:

```python
from app.files.manager import FileManager
from app.files.models import FileObject
from app.files.providers import S3FileProvider

__all__ = [
    "FileManager",
    "FileObject",
    "S3FileProvider",
]
```

## `blueprint.py`

Where a module exposes HTTP routes, `blueprint.py` should define its Flask blueprint.

Example:

```python
from flask import Blueprint

files_bp = Blueprint(
    "files",
    __name__,
    template_folder="templates",
)
```

Blueprint construction should remain separate from substantial route logic.

## `routes.py`

Routes should:

* authenticate the request;
* check permissions;
* extract request input;
* call services;
* translate application exceptions into HTTP responses;
* return templates, redirects or structured responses.

Routes should not:

* contain significant business rules;
* create complex model graphs directly;
* call infrastructure clients;
* manage multi-step transactions;
* duplicate validation already provided by a service.

## `models.py`

Models define persistent domain state and relationships.

Models may contain:

* simple derived properties;
* narrowly scoped invariant checks;
* display helpers;
* representation methods.

Models should not:

* call external services;
* send notifications;
* access Flask request context;
* perform unrelated database queries through global session access;
* contain large workflow implementations.

Complex operations belong in services.

## `services.py`

Services contain application and domain workflows.

Services may:

* coordinate multiple models;
* manage transactions;
* call platform capabilities;
* enforce business rules;
* raise application-specific exceptions;
* schedule asynchronous tasks;
* create audit events.

Services should expose explicit methods with clear inputs and outputs.

## `forms.py`

Forms define request-level input validation and field presentation.

Forms should not contain substantial business behaviour.

A form being valid does not replace service-layer validation.

The service must remain safe when called outside an HTTP request.

## `validators.py`

Validators contain reusable validation that does not naturally belong to one form.

Examples include:

* catalogue-driven file validation;
* competency date validation;
* identifier formatting;
* model-independent data checks.

Validation errors should use application-defined exceptions or structured results.

## `exceptions.py`

Each module should define exceptions meaningful to callers.

Example:

```python
class CompetencyError(Exception):
    pass


class CompetencyNotFoundError(CompetencyError):
    pass


class InvalidCompetencyStateError(CompetencyError):
    pass
```

Third-party exceptions should not escape the module's public service interface without deliberate reason.

## `permissions.py`

Permission definitions and helper checks should be centralised.

Stable permission codes should be declared in one clear location.

Example:

```python
VIEW_COMPETENCIES = "competencies:view"
MANAGE_COMPETENCIES = "competencies:manage"
```

Display labels may change, but permission codes must remain stable.

## `seeds.py`

Seed and reference-data logic should be:

* safe to run repeatedly;
* based on stable codes;
* upgrade-aware;
* careful not to overwrite local display customisations unnecessarily.

Seed logic should not be embedded in page-load routes.

## `tasks.py`

Celery tasks should be thin wrappers around reusable services.

Tasks must be idempotent.

A task should not contain business logic that cannot also be called synchronously in tests.

Example:

```python
@celery.task
def generate_thumbnail(file_id: str) -> None:
    thumbnail_service.generate(UUID(file_id))
```

## `templates/`

Templates should be namespaced by module.

Example:

```text
templates/
└── competencies/
    ├── index.html
    ├── form.html
    └── _table.html
```

Generic shared components should live in a shared template component location rather than being copied between modules.

## `static/`

Module-specific static files should be namespaced.

Shared styles, scripts and components belong in the global design system.

## `tests/`

Tests should normally mirror the module structure.

Example:

```text
tests/
└── competencies/
    ├── test_models.py
    ├── test_services.py
    ├── test_routes.py
    └── test_permissions.py
```

# Public and private module interfaces

A module should deliberately distinguish between supported public interfaces and internal implementation details.

## Public interface

Other modules may depend on:

* documented service methods;
* stable model identifiers where necessary;
* published exceptions;
* stable permission codes;
* declared events or task interfaces.

## Private implementation

Other modules should not depend on:

* internal helper functions;
* undocumented query construction;
* private model state;
* route implementation details;
* provider-specific clients;
* internal template fragments.

Python naming conventions such as a leading underscore should be used where helpful, but architectural discipline is more important than naming alone.

# Cross-module access

## Preferred approach

A module needing another module's behaviour should call its service.

Example:

```python
person = people_service.get_person(person_id)
```

rather than:

```python
person = db.session.get(Person, person_id)
```

when the caller depends on People module business rules.

## Permitted direct relationships

Direct foreign keys between modules are sometimes appropriate.

Examples include:

* a competency record referencing a person;
* a file audit event referencing a user;
* a library version referencing a `FileObject`.

A foreign key does not grant permission to manipulate the related module's records directly.

The owning module still controls lifecycle and business behaviour.

## Avoid bidirectional coupling

Two modules should not both depend heavily on each other's services.

Where circular dependency appears, consider extracting a shared capability or introducing an event-based interaction.

# Module ownership

The module that owns a record controls:

* creation;
* mutation;
* validation;
* lifecycle transitions;
* deletion or archival;
* audit semantics;
* permission rules.

Examples:

* Files owns `FileObject`.
* Competencies owns competency assignments and renewals.
* Library owns document approval and publication.
* People owns person identity records.
* Auth owns accounts, roles and permissions.

A consuming module may reference an owned record but should not redefine its lifecycle.

# Database transaction ownership

The service performing a business workflow should normally own its transaction.

Routes should not scatter commits across multiple calls.

Preferred:

```python
competency_service.assign_and_attach_evidence(...)
```

Avoid:

```python
db.session.add(record)
db.session.commit()

file_object = file_manager.create_file(...)
record.file_object_id = file_object.id
db.session.commit()
```

Multi-step workflows should define compensation behaviour where one system cannot participate in the database transaction, such as S3 uploads.

# Flask application startup

Application startup should:

* load configuration;
* initialise extensions;
* register blueprints;
* register CLI commands;
* import models required by migration metadata.

Application startup should not:

* create buckets from every worker process;
* seed data through page requests;
* perform long-running network checks;
* execute destructive migrations;
* depend on optional external services being available unless required for basic startup.

Explicit CLI commands should be used for deployment-time initialisation where appropriate.

# CLI command conventions

CLI commands should be:

* safe to repeat where practical;
* explicit about their effects;
* implemented through application services;
* suitable for Docker-based deployment.

Examples:

```text
flask files-init
flask reference-data-sync
flask create-admin
```

Commands should return useful success and failure messages and should fail with a non-zero exit code when the operation cannot complete.

# Naming conventions

## Package names

Use lowercase singular or collective names that clearly describe the domain.

Examples:

```text
files
people
competencies
library
notifications
```

Avoid ambiguous abbreviations.

## Model names

Use singular PascalCase names.

Examples:

```python
FileObject
CompetencyType
LibraryDocument
```

## Table names

Use lowercase plural snake_case names.

Examples:

```text
file_objects
competency_types
library_documents
```

## Service names

Use names describing the owned capability.

Examples:

```python
FileManager
CompetencyService
AuditService
ReferenceDataService
```

Avoid vague names such as `Helper`, `UtilsService` or `Manager` where the managed responsibility is unclear.

## Stable codes

Use lowercase snake_case.

Examples:

```text
mandatory_training
profile_photo
clinical_grade
vehicle_insurance
```

## Permission codes

Use a stable namespace and action.

Examples:

```text
files:view
files:manage
competencies:view
competencies:assign
library:approve
```

# Imports

Imports should reflect module boundaries.

Preferred:

```python
from app.files import get_file_manager
```

Avoid importing internal provider implementations into business modules:

```python
from app.files.providers.s3 import S3FileProvider
```

Provider imports are appropriate only inside the Files platform package and application composition code.

# Avoid generic utility dumping grounds

Files such as these should be avoided:

```text
utils.py
helpers.py
common.py
misc.py
```

unless their scope is tightly defined.

A function should live with the capability that owns it.

For example:

* content-disposition helpers belong in `files/http.py`;
* object-key generation belongs in `files/keys.py`;
* competency date rules belong in `competencies/validators.py`.

# Events and asynchronous boundaries

Modules may communicate through asynchronous tasks or future domain events where immediate coupling is undesirable.

Examples include:

* file uploaded;
* competency expiring;
* policy published;
* equipment service due.

Event payloads should contain stable identifiers, not full mutable model representations.

Consumers must handle repeated delivery safely.

# Optional modules

Future optional modules should depend only on documented platform interfaces.

The core platform must not import optional domain modules merely to start successfully.

Optional modules may register:

* blueprints;
* permissions;
* reference data;
* catalogue definitions;
* navigation entries;
* reports;
* workflows.

A formal plugin system is not required yet, but current architecture should avoid preventing one later.

# New module checklist

Before creating a new module, determine:

1. Is this a platform capability, shared domain module or business module?
2. Does an existing module already own the concept?
3. Can the requirement be handled by extending an existing service?
4. Does another future module likely need the same capability?
5. What stable codes and permissions are required?
6. What records does the module own?
7. Which other modules may it reference?
8. What audit events are significant?
9. What reference data is needed?
10. What tests define its expected behaviour?

# Minimum module completion standard

A module is not complete solely because its primary page works.

Where applicable, it should include:

* models and migrations;
* service-layer workflows;
* validation;
* permission enforcement;
* audit integration;
* seed or reference data;
* HTMX and full-page behaviour;
* empty and error states;
* tests;
* architecture or developer documentation;
* Docker-compatible operation.

# Architecture decision: package-based capability ownership

## Decision

Response Connect will organise application behaviour around capability and domain packages with explicit ownership and service boundaries.

## Context

As the application grows, placing unrelated logic in routes or importing models directly across the codebase would create tight coupling and inconsistent implementation patterns.

The project needs a structure that remains understandable to external contributors and supports future optional modules.

## Alternatives considered

### Large monolithic blueprint packages

This would be simple initially but would mix routes, workflows, infrastructure access and domain logic.

### Technical-layer-only structure

A structure such as global `models/`, `routes/` and `services/` directories would group files by technical type rather than business ownership, making modules difficult to isolate.

### Microservices

Separate deployable services would create excessive operational complexity for the current self-hosted deployment model.

## Consequences

Benefits:

* clear ownership;
* easier testing;
* more predictable navigation;
* reduced cross-module coupling;
* better preparation for optional modules;
* stable platform interfaces.

Trade-offs:

* some workflows require explicit service coordination;
* contributors must understand module boundaries;
* careful import design is required;
* direct model access may occasionally appear simpler but should be resisted when business rules are involved.

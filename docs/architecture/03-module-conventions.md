# Module Conventions

## Purpose

This document defines how Response Connect modules should be designed, structured, registered, tested and maintained.

It provides the standard pattern contributors should follow when adding a new capability or extending an existing one.

The objective is not to force every package to contain identical files. The objective is to ensure that modules have:

* clear ownership;
* predictable structure;
* explicit public interfaces;
* consistent service boundaries;
* appropriate permissions;
* upgrade-safe reference data;
* reusable user-interface patterns;
* adequate tests and documentation.

A contributor should be able to read this document and understand how to build a module that feels native to Response Connect.

# What is a module?

A module is a package that owns a coherent platform capability, shared domain concept or business capability.

Examples include:

```text
files
catalogues
audit
people
competencies
library
vehicles
equipment
incidents
```

A module should have a clear answer to the question:

> What capability or business concept does this package own?

Modules should not be created merely to group code by technical type.

Avoid modules such as:

```text
utils
helpers
common
database
pdf
misc
```

unless the name represents a tightly defined capability rather than a general dumping ground.

# Module classifications

Every module should be classified as one of the following.

## Platform capability

A platform capability provides application-wide behaviour reused by many modules.

Examples include:

* authentication;
* permissions;
* catalogues;
* files;
* audit;
* reference data;
* notifications;
* workflow;
* search;
* reporting.

Platform capabilities should expose stable service interfaces and should not contain business logic specific to one operational module.

## Shared domain module

A shared domain module owns a concept used by several business areas.

Examples include:

* people;
* organisations;
* locations;
* competencies;
* tasks;
* vehicles;
* equipment;
* library records.

A shared domain module may use platform capabilities but should remain independent of one narrow operational workflow.

## Business module

A business module implements workflows for a particular operational area.

Examples include:

* recruitment;
* event medical operations;
* patient transport;
* shift management;
* incident management;
* clinical activity;
* fleet operations.

Business modules should reuse platform and shared domain services rather than reimplementing them.

# Before creating a new module

Before adding a module, answer the following questions.

1. Does an existing module already own this concept?
2. Can the requirement be implemented by extending an existing public service?
3. Is the proposed module a capability, shared domain concept or business workflow?
4. Could several modules reuse this functionality?
5. Would the proposed package create a second way of performing an existing operation?
6. What records and lifecycle transitions would the module own?
7. Which other modules would it depend on?
8. Can those dependencies be expressed through public service interfaces?
9. What stable codes, permissions or reference data are required?
10. What would explicitly remain outside the module’s responsibility?

A new module should not be created merely because a feature needs a new page.

# Module ownership

Every module must explicitly define what it owns.

Ownership includes:

* database records;
* business rules;
* lifecycle transitions;
* validation;
* service interfaces;
* permission semantics;
* audit semantics;
* reference data;
* asynchronous tasks;
* module-specific templates;
* module-specific tests.

The owning module controls how its records are:

* created;
* changed;
* activated or deactivated;
* approved;
* archived;
* deleted;
* restored;
* purged.

Other modules may reference an owned record but must not redefine its lifecycle.

## Ownership example: Files

The Files module owns:

* immutable file records;
* storage providers;
* file-type rules;
* upload validation;
* download streaming;
* file derivatives;
* file version containers;
* scanning state;
* file audit semantics.

The Files module does not own:

* mandatory training;
* competency validity;
* policy approval;
* incident access rules;
* staff records.

Those modules reference files through the Files module’s public interfaces.

## Ownership example: Library

The Library module may own:

* document identity;
* document categories;
* review and approval;
* publication;
* effective and review dates;
* document version history;
* supersession.

The Library module does not own:

* S3 object storage;
* binary upload processing;
* user authentication;
* generic audit persistence.

It uses the Files, Authentication and Audit capabilities.

# What a module does not do

Every significant module should document both:

* what it owns;
* what it deliberately does not own.

This prevents modules from gradually absorbing unrelated responsibilities.

A module should not become the default home for functionality simply because it was convenient to add code there.

When a module starts to manage unrelated concepts, contributors should consider:

* moving functionality to an existing platform capability;
* extracting a new shared capability;
* introducing an application workflow service;
* correcting an unclear ownership boundary.

# Standard module structure

A mature module may use the following structure:

```text
module_name/
├── __init__.py
├── blueprint.py
├── routes.py
├── models.py
├── services.py
├── forms.py
├── validators.py
├── exceptions.py
├── permissions.py
├── seeds.py
├── tasks.py
├── events.py
├── templates/
│   └── module_name/
├── static/
│   └── module_name/
└── tests/
```

Not every module needs every file.

Files must be added because the responsibility exists, not to satisfy an empty directory convention.

# Package initializer

The module’s `__init__.py` defines its intended public Python interface.

It may export:

* service factories;
* public service classes;
* public exceptions;
* selected public models;
* stable permission constants;
* the blueprint where appropriate.

Example:

```python
from app.files.manager import FileManager
from app.files.models import FileObject
from app.files.providers import FileProvider
from app.files.services import get_file_manager

__all__ = [
    "FileManager",
    "FileObject",
    "FileProvider",
    "get_file_manager",
]
```

The initializer should not:

* perform database writes;
* run seed operations;
* make network calls;
* create external resources;
* contain business workflows;
* hide circular imports caused by unclear module boundaries.

# Blueprint registration

A module exposing HTTP routes should define one or more Flask blueprints.

Blueprint creation should normally live in `blueprint.py` or a small package initializer.

Example:

```python
from flask import Blueprint

catalogues_bp = Blueprint(
    "catalogues",
    __name__,
    template_folder="templates",
)
```

Blueprint registration belongs in application composition, normally `create_app()`.

Importing a module should not automatically register its blueprint through hidden side effects.

A module may have more than one blueprint where there is a clear boundary, such as:

* authenticated application routes;
* external or public routes;
* API routes.

Multiple blueprints should not be used merely to split a large route file.

# Routes

Routes are HTTP adapters.

A route should normally:

1. authenticate the user;
2. check the relevant permission;
3. parse request data;
4. validate request-level fields;
5. call a public service;
6. translate known exceptions into an HTTP response;
7. return a template, redirect or structured response.

Routes should not:

* call infrastructure clients directly;
* contain substantial business logic;
* manage multi-step database transactions;
* duplicate service validation;
* construct complex object graphs;
* alter another module’s records directly;
* contain long-running processing.

Preferred:

```python
@files_bp.post("/types")
@login_required
@permission_required("files:manage_types")
def create_file_type():
    form = FileTypeForm()

    if not form.validate_on_submit():
        return render_template(
            "files/types/_form.html",
            form=form,
        ), 422

    try:
        file_type = get_file_type_service().create(
            code=form.code.data,
            name=form.name.data,
            created_by_id=current_user.id,
        )
    except DuplicateFileTypeCodeError:
        form.code.errors.append(
            "A file type with this code already exists."
        )
        return render_template(
            "files/types/_form.html",
            form=form,
        ), 422

    return redirect(
        url_for(
            "files.view_file_type",
            file_type_id=file_type.id,
        )
    )
```

# Models

A module owns the models declared within it.

Models should contain:

* field definitions;
* database constraints;
* relationships;
* simple derived properties;
* small invariant helpers;
* `__repr__()` methods.

Models should not:

* call infrastructure services;
* read from Flask request context;
* send notifications;
* schedule Celery tasks;
* implement large workflows;
* make unrelated database queries;
* contain permission logic tied to the current user.

Model methods should remain focused on the record itself.

Example:

```python
@property
def is_deleted(self) -> bool:
    return self.deleted_at is not None
```

A multi-record workflow belongs in a service.

# Services

Services own business and application workflows.

A module should expose services for operations that involve:

* business rules;
* lifecycle transitions;
* multiple records;
* transactions;
* audit events;
* notifications;
* file management;
* asynchronous work;
* coordination with another capability.

Services should raise application-defined exceptions.

Routes, tasks and CLI commands should call the same services where practical.

Detailed service conventions are defined in:

```text
04-service-layer-conventions.md
```

# Forms

Forms handle request-level field validation and rendering concerns.

Forms may validate:

* required fields;
* basic string lengths;
* simple formats;
* valid choices;
* CSRF protection.

Forms should not be the only enforcement of a business rule.

A service must remain safe when called by:

* an HTTP route;
* a CLI command;
* a Celery task;
* an API endpoint;
* a test.

Form choices based on database state should be loaded deliberately and should not cause uncontrolled queries at import time.

# Validators

Reusable validation that is not tied to one HTTP form belongs in `validators.py`.

Examples include:

* filename validation;
* catalogue-code validation;
* date-range validation;
* competency expiry validation;
* file-type rule validation;
* identifier normalisation.

Validators should generally:

* accept explicit inputs;
* avoid HTTP context;
* avoid persistence unless specifically designed as a database validator;
* produce clear errors;
* be reusable from services and tests.

A validator should not mutate unrelated records.

# Exceptions

Every module should define exceptions meaningful to its callers.

Example:

```python
class FileTypeError(Exception):
    """Base exception for file-type operations."""


class FileTypeNotFoundError(FileTypeError):
    """Raised when a file type cannot be found."""


class DuplicateFileTypeCodeError(FileTypeError):
    """Raised when a stable code is already in use."""


class FileTypePersistenceError(FileTypeError):
    """Raised when a file type cannot be saved."""
```

Routes should not need to understand raw:

* SQLAlchemy exceptions;
* provider exceptions;
* Redis exceptions;
* Celery exceptions;
* storage-client exceptions.

Third-party exceptions should normally be retained through exception chaining and appropriate logging.

# Permissions

Every user-facing module should define stable permission codes.

Permission codes should normally use:

```text
module:action
```

Examples:

```text
files:view
files:upload
files:download
files:delete
files:manage_types
library:view
library:manage
library:approve
competencies:view
competencies:assign
competencies:verify
```

Permission codes:

* are stable internal identifiers;
* should not depend on route names;
* should not use editable display labels;
* should be declared centrally in the owning module;
* should be included in the permission catalogue.

Example:

```python
VIEW_FILES = "files:view"
UPLOAD_FILES = "files:upload"
MANAGE_FILE_TYPES = "files:manage_types"
```

Routes should use the declared constant where practical rather than repeating string literals.

# Permission enforcement

Permissions must be checked at the application boundary.

A user obtaining a UUID or route URL must not bypass authorisation.

Routes should check:

* authentication;
* permission code;
* ownership or access scope;
* record lifecycle state.

Services may also enforce explicit authorisation where the rule is part of the business workflow or where the service is used outside HTTP.

Services should not depend implicitly on `current_user`.

Preferred:

```python
service.approve(
    document_id=document_id,
    approved_by_id=current_user.id,
)
```

# Audit integration

Significant module actions must use the shared Audit capability.

Examples include:

* creating a record;
* changing a stable configuration;
* activating or deactivating a catalogue item;
* uploading a file;
* downloading a sensitive file;
* deleting or restoring a record;
* approving or rejecting;
* assigning or removing a competency;
* changing permissions.

A module owns the meaning of its audit events.

The Audit module owns:

* event persistence;
* common event fields;
* actor identity;
* request context capture;
* querying and display infrastructure.

Modules should not create their own unrelated audit tables.

# Reference data and seed behaviour

A module requiring system-provided records should define them through upgrade-safe reference-data or seed logic.

Reference records must use stable codes.

Seed operations must be:

* idempotent;
* safe to run repeatedly;
* able to distinguish system and custom records;
* careful not to overwrite local display customisations;
* explicit about fields owned by the system;
* suitable for deployment and upgrades.

Seed logic must not run implicitly when a user opens a page.

Preferred deployment command:

```text
flask reference-data-sync
```

Temporary module-specific commands may exist while the shared framework is being built.

# Catalogues

Configurable lookup data should use the shared Catalogue Framework.

A module should not create an unrelated CRUD implementation for:

* types;
* categories;
* statuses;
* classifications;
* reasons;
* priorities.

Catalogue records should normally support:

* UUID identifiers;
* stable codes;
* display names;
* descriptions;
* icons;
* colours;
* sort order;
* active state;
* system/custom distinction.

The Catalogue Framework chapter defines the final conventions.

# Tasks

Celery tasks should be thin adapters around reusable services.

Preferred:

```python
@celery.task
def scan_file(file_id: str) -> None:
    get_file_scan_service().scan(
        UUID(file_id)
    )
```

Avoid placing the full workflow inside the task function.

Tasks must be idempotent.

Tasks should accept stable identifiers rather than serialised SQLAlchemy models.

A task must consider:

* repeated delivery;
* retries;
* partial completion;
* worker interruption;
* record deletion;
* stale state.

# Events

Modules may eventually publish domain events for loosely coupled behaviour.

Examples include:

```text
file.uploaded
file.scan_completed
competency.expiring
library.document_published
person.created
```

Event payloads should contain stable identifiers and essential immutable context.

Events should not expose full mutable model dictionaries by default.

Event consumers must handle duplicate delivery safely.

Until a formal event framework exists, modules should not invent incompatible local event systems.

# Templates

Templates must be namespaced by module.

Example:

```text
templates/
└── files/
    ├── index.html
    ├── detail.html
    ├── types/
    │   ├── index.html
    │   ├── _table.html
    │   └── _form.html
    └── components/
        └── _file_picker.html
```

Shared application components should be moved to a shared design-system or component location.

Templates should not duplicate complex business rules.

The service or route should provide the state required for display.

# HTMX behaviour

HTMX is an enhancement to the standard application flow, not a separate application architecture.

Where practical, a page should support:

* normal full-page requests;
* HTMX partial updates;
* server-side validation;
* accessible error messages;
* predictable browser history;
* meaningful URLs.

A route may return different templates based on whether the request is an HTMX request, but business behaviour must remain the same.

Example:

```python
if request.headers.get("HX-Request"):
    return render_template(
        "catalogues/_table.html",
        records=records,
    )

return render_template(
    "catalogues/index.html",
    records=records,
)
```

Avoid creating separate duplicated routes solely for HTMX where one route can serve both safely.

# Static assets

Module-specific assets should be namespaced.

Example:

```text
static/
└── files/
    ├── files.css
    └── files.js
```

Reusable styling and behaviour should live in the shared design system.

Module JavaScript should be kept minimal.

Server-rendered HTML and HTMX should remain the preferred interaction model.

# Navigation registration

A module exposing user-facing pages should declare its navigation requirements clearly.

Navigation entries should define:

* stable identifier;
* label;
* icon;
* route;
* required permission;
* section;
* sort order;
* optional feature flag.

Navigation should not be scattered across unrelated templates.

A shared navigation registry may be introduced later. New modules should be designed so they can participate in one.

# Configuration

A module may define configuration values for deployment or application behaviour.

Configuration should:

* use clear environment-variable names;
* provide safe defaults where appropriate;
* be documented;
* avoid hard-coded secrets;
* be loaded centrally through application configuration;
* be passed into services through factories.

Business modules should not read arbitrary environment variables throughout their code.

Preferred:

```python
FILE_UPLOAD_MAX_BYTES = int(
    os.getenv(
        "FILE_UPLOAD_MAX_BYTES",
        "26214400",
    )
)
```

Services should receive the configured value rather than repeatedly reading the environment.

# Feature flags

Feature flags may be used for:

* optional modules;
* staged rollout;
* incomplete platform capabilities;
* installation-specific functionality.

Feature flags must not be used indefinitely to preserve two conflicting implementations of the same capability.

A flag should have:

* stable name;
* documented default;
* defined removal or stabilisation plan;
* tests for relevant enabled and disabled behaviour.

# Database migrations

Each module owns migrations affecting its records, even though all migrations are stored in the shared Alembic history.

A migration should:

* have a clear message;
* contain only intended changes;
* preserve existing data;
* consider upgrade and downgrade behaviour;
* avoid unexplained alterations to unrelated tables;
* be reviewed before application.

Reference-data changes and schema changes should not be confused.

A migration changes database structure or transforms stored data.

A reference-data synchronisation updates upgrade-managed catalogue content.

# Model discovery

Models must be imported during application startup so Flask-Migrate can discover them.

This may be done through explicit imports in application composition.

Example:

```python
from app.files.models import FileObject  # noqa: F401
```

The import exists to register SQLAlchemy metadata and should be commented or marked appropriately where linting requires it.

Avoid relying on accidental imports from route registration.

# CLI commands

Module CLI commands should:

* call public services;
* be safe to repeat where practical;
* provide clear output;
* return failure status when unsuccessful;
* work inside the Docker deployment;
* avoid duplicating business logic.

Example:

```text
flask files-init
flask reference-data-sync
flask create-admin
```

Deployment-time initialisation should use explicit commands rather than page-load side effects.

# Tests

Each module should include tests appropriate to its responsibilities.

Typical test groups include:

```text
tests/
├── test_models.py
├── test_services.py
├── test_routes.py
├── test_permissions.py
├── test_tasks.py
├── test_reference_data.py
└── test_migrations.py
```

Not every module needs every group.

Tests should cover:

* successful workflows;
* validation failures;
* duplicate stable codes;
* missing records;
* inactive and deleted state;
* permission failures;
* transaction rollback;
* external compensation;
* idempotency;
* audit creation;
* HTMX and full-page responses;
* important accessibility-relevant output.

Service tests should be the primary location for business-rule testing.

Route tests should focus on HTTP behaviour, permission enforcement and response rendering.

# Test isolation

Tests should not depend on:

* execution order;
* permanent MinIO objects;
* shared mutable global state;
* a previously run seed command;
* local developer data.

Tests involving external providers should use:

* a fake provider for service tests;
* isolated integration resources for provider tests;
* cleanup that runs even when assertions fail.

Stable test factories and fixtures should be preferred over repeated ad hoc setup.

# Documentation

A module should document:

* its responsibility;
* its public interfaces;
* its stable permission codes;
* its reference data;
* its configuration;
* its important lifecycle states;
* its significant architecture decisions;
* examples of correct use.

Platform capabilities should have both:

* architecture documentation explaining why they exist;
* developer documentation explaining how to use them.

User-facing modules will also require user and administrator documentation later.

# Module maturity

Modules may progress through maturity levels.

## Level 1 — Functional

The module’s primary workflow works.

It has:

* initial models;
* migration;
* basic routes or service;
* minimum validation.

Level 1 is not considered production-complete.

## Level 2 — Structured

The module follows the standard architecture.

It has:

* service-layer workflows;
* permissions;
* application exceptions;
* module ownership boundaries;
* appropriate tests.

## Level 3 — Integrated

The module uses shared platform capabilities.

It has:

* audit integration;
* catalogue or reference-data integration;
* notification or workflow integration where needed;
* reusable UI patterns;
* documented configuration.

## Level 4 — Extensible

The module is suitable for broader reuse.

It has:

* clear public interfaces;
* stable codes;
* upgrade-safe behaviour;
* idempotent tasks;
* integration documentation;
* comprehensive lifecycle tests.

## Level 5 — Reference implementation

The module demonstrates the preferred Response Connect patterns and may be used as an example by contributors.

A Level 5 module should be:

* reliable;
* well documented;
* thoroughly tested;
* consistent with the handbook;
* accessible;
* upgrade safe;
* reusable;
* free of known architectural shortcuts.

The Files module should become the first Level 5 platform module.

# Optional modules

Future optional modules must not be required for the core application to start.

An optional module may register:

* blueprints;
* permissions;
* navigation entries;
* catalogue definitions;
* reference data;
* tasks;
* reports;
* workflows.

Core platform modules should not import optional business modules directly.

Optional modules should depend on documented platform interfaces.

A formal plugin system is not required yet, but new architecture should avoid making one impossible later.

# Cross-module communication

Modules should communicate through public services.

Preferred:

```python
file_object = get_file_manager().create_from_filestorage(
    upload,
    uploaded_by_id=user_id,
)
```

Avoid:

```python
provider = S3FileProvider(...)
provider.upload_fileobj(...)
db.session.add(FileObject(...))
```

from a business module.

Direct foreign keys between modules are allowed where the relationship is meaningful.

A direct foreign key does not grant lifecycle ownership.

For example, a competency-evidence record may reference `FileObject.id`, but the Competencies module must not overwrite or purge the underlying file directly.

# Workflow services

Where a user action coordinates several modules, introduce a higher-level workflow service.

Example:

```python
class MandatoryTrainingUploadWorkflow:
    def complete_training(
        self,
        *,
        person_id: UUID,
        competency_type_id: UUID,
        upload: FileStorage,
        completed_at: date,
        actor_id: UUID,
    ) -> CompetencyRecord:
        ...
```

This service may coordinate:

* Files;
* Competencies;
* Audit;
* Notifications.

The route should not implement that coordination itself.

# Dependency direction

Dependencies should generally flow downward:

```text
Business modules
        ↓
Shared domain modules
        ↓
Platform capabilities
        ↓
Infrastructure providers
```

Platform capabilities should not depend on business modules.

Where two peer modules need each other heavily, consider:

* extracting a shared capability;
* adding a workflow service above both;
* using a future domain event;
* revisiting ownership.

Circular imports are often a warning that dependency direction is unclear.

# Avoiding duplicate patterns

Before introducing a helper, service, component or workflow, search for the existing project pattern.

A contributor should not add:

* a second upload manager;
* another audit table;
* a new catalogue page architecture;
* a custom notification transport;
* an alternative modal framework;
* a second permission-decorator pattern.

Where the existing pattern is inadequate, improve or replace it intentionally and update the handbook.

Do not preserve two patterns indefinitely merely to avoid refactoring.

# Definition of Done

A module or significant module capability is complete only when all applicable items have been considered.

## Architecture and ownership

* [ ] The module classification is clear.
* [ ] The module’s owned records and responsibilities are documented.
* [ ] The module explicitly states what it does not own.
* [ ] Cross-module dependencies use public interfaces.
* [ ] No duplicate platform capability has been introduced.
* [ ] Significant architecture decisions are recorded.

## Database

* [ ] Models use project conventions.
* [ ] Database constraints protect structural integrity.
* [ ] Migrations have been generated and inspected.
* [ ] Existing installation data is preserved.
* [ ] Stable codes are used for reference records.
* [ ] Seed or reference-data logic is idempotent.

## Services and validation

* [ ] Business logic is implemented in services.
* [ ] Transaction ownership is clear.
* [ ] Application exceptions are defined.
* [ ] Service-level validation exists.
* [ ] External side effects have compensation behaviour.
* [ ] Asynchronous operations are idempotent.

## Security

* [ ] Permissions use stable codes.
* [ ] Routes enforce authentication and authorisation.
* [ ] Record ownership or access scope is checked.
* [ ] Sensitive information is not exposed in logs or errors.
* [ ] Uploaded files use the Files capability.
* [ ] Direct infrastructure access is avoided.

## Audit and lifecycle

* [ ] Significant actions create audit events.
* [ ] Lifecycle transitions use explicit service methods.
* [ ] Deletion, restoration and purge behaviour are defined.
* [ ] Retention implications have been considered.
* [ ] State transitions are tested.

## User interface

* [ ] Full-page behaviour works.
* [ ] HTMX behaviour works where used.
* [ ] Validation errors are clearly displayed.
* [ ] Empty states are present.
* [ ] Loading and failure states are handled.
* [ ] Permission-restricted actions are not shown incorrectly.
* [ ] The interface uses shared design patterns.
* [ ] Accessibility has been considered.

## Testing

* [ ] Service success paths are tested.
* [ ] Validation failures are tested.
* [ ] Permission failures are tested.
* [ ] Missing and inactive records are tested.
* [ ] Transaction rollback is tested.
* [ ] External compensation is tested where relevant.
* [ ] Task idempotency is tested.
* [ ] HTMX and full-page routes are tested.
* [ ] Tests are isolated and repeatable.

## Operations

* [ ] Configuration is documented.
* [ ] Docker deployment works.
* [ ] CLI commands are repeatable where appropriate.
* [ ] Upgrade behaviour is understood.
* [ ] Logs are useful and safe.
* [ ] Optional external dependencies fail clearly.

## Documentation

* [ ] Public service interfaces are documented.
* [ ] Permissions are documented.
* [ ] Reference data is documented.
* [ ] Architecture guidance is updated.
* [ ] User or administrator documentation is planned where applicable.
* [ ] The module has an appropriate maturity level.

# Module review questions

A reviewer should ask:

1. Is the module’s ownership obvious?
2. Does the package contain behaviour that belongs elsewhere?
3. Has an existing capability been duplicated?
4. Does business logic live in services?
5. Are module boundaries respected?
6. Are stable codes used?
7. Are permissions explicit?
8. Are significant actions audited?
9. Are tasks idempotent?
10. Are migrations upgrade safe?
11. Can the module be tested without HTTP?
12. Does the UI follow existing patterns?
13. Is the module suitable for self-hosted deployment?
14. Can another contributor understand how to extend it?
15. Does the implementation strengthen the platform?

# If you are unsure

When the correct design is unclear:

* choose the simpler implementation;
* reuse an existing capability;
* keep business logic in services;
* preserve module ownership;
* prefer explicit behaviour;
* use stable codes;
* protect upgrade safety;
* consider whether another module will need the same functionality;
* avoid introducing a second pattern;
* document any genuinely new architectural choice.

# Architecture decision: standard module conventions

## Decision

Response Connect modules will follow a consistent ownership, structure, public-interface and completion model.

Modules may vary in size, but they must use the same architectural principles and shared platform capabilities.

## Context

As the application expands, inconsistent module design would lead to duplicated services, unclear ownership, tightly coupled models and unpredictable contributor experience.

The project requires a standard that defines not only file placement, but how a module participates in permissions, audit, reference data, HTMX, testing and upgrades.

## Alternatives considered

### Allow each module to define its own conventions

This would provide local flexibility but would create inconsistent code and increase maintenance cost.

### Enforce identical package contents for every module

This would be predictable but would create unnecessary empty files and boilerplate.

### Organise only by technical layer

Global model, route and service directories would obscure domain ownership and make optional modules difficult to isolate.

## Consequences

Benefits:

* predictable contributor experience;
* clearer ownership;
* reduced duplication;
* consistent reviews;
* easier testing;
* improved upgrade safety;
* stronger preparation for optional modules.

Trade-offs:

* contributors must understand and follow the handbook;
* simple features may require more deliberate structure;
* existing early modules may need gradual refactoring;
* architecture review becomes part of feature development.

# Related documents

* [Platform Principles](01-platform-principles.md)
* [Project Structure and Module Boundaries](02-project-structure.md)
* [Service-Layer Conventions](04-service-layer-conventions.md)

# Future considerations

The following are intentionally deferred:

* formal plugin registration;
* shared navigation registry;
* domain-event framework;
* feature-flag service;
* module manifest format;
* automated architecture checks;
* module scaffolding CLI;
* platform-readiness reporting.

These should be introduced only when the current architecture provides enough real implementations to define reliable abstractions.

# Review checklist

When reviewing a module against this chapter, confirm:

* its ownership is clear;
* its public interface is deliberate;
* routes remain thin;
* business workflows use services;
* infrastructure access is abstracted;
* permissions and audit semantics exist;
* reference data is upgrade safe;
* UI behaviour follows shared patterns;
* tests cover public behaviour;
* operational deployment remains simple;
* the module does not introduce a competing pattern.

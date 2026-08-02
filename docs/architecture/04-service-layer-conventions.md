# Service-Layer Conventions

## Purpose

This document defines how application services should be designed, called and tested throughout Response Connect.

Services provide the main boundary between HTTP routes, asynchronous tasks, domain models and infrastructure capabilities.

A well-designed service should make business behaviour:

* reusable outside Flask routes;
* testable without HTTP;
* consistent across synchronous and asynchronous execution;
* resistant to partial failure;
* independent of provider-specific libraries;
* clear to future contributors.

# What belongs in a service

A service should own a meaningful application or domain capability.

Examples include:

```python
FileManager
CompetencyService
CatalogueService
AuditService
ReferenceDataService
NotificationService
LibraryService
```

Services commonly perform one or more of the following:

* enforce business rules;
* coordinate multiple models;
* manage a database transaction;
* call another platform capability;
* translate third-party failures into application exceptions;
* create audit events;
* schedule asynchronous work;
* perform lifecycle transitions;
* return domain records or structured results.

# What does not belong in a service

Services should not become general-purpose dumping grounds.

Avoid vague classes such as:

```python
HelperService
CommonService
UtilityManager
ApplicationTools
```

A service should have a clear owner and responsibility.

Small pure functions may belong in:

* `validators.py`;
* `keys.py`;
* `http.py`;
* a narrowly scoped module helper file.

Not every function requires a class.

# Public service interfaces

A module should expose only the service methods intended for other modules.

Example:

```python
class CompetencyService:
    def assign(
        self,
        *,
        person_id: UUID,
        competency_type_id: UUID,
        awarded_at: datetime,
        expires_at: datetime | None,
        evidence_file_ids: list[UUID],
        assigned_by_id: UUID,
    ) -> CompetencyRecord:
        ...
```

A public method should make clear:

* required inputs;
* optional inputs;
* returned value;
* exceptions callers should handle;
* whether it commits;
* significant side effects.

Private implementation helpers should use a leading underscore.

# Service contract principle

Public domain services must expose predictable contracts.

Every public service method must either:

* return the requested domain object, collection or structured result; or
* raise a domain-specific exception describing why the operation could not be completed.

Public mutation methods must not:

* return `None` to indicate failure;
* return boolean success or failure flags;
* return undocumented sentinel values;
* expose raw persistence exceptions;
* expose provider-specific exceptions.

Preferred:

```python
desk = desk_service.create(command)
```

The method returns the created `Desk` or raises a Desk-specific exception.

Preferred:

```python
desk = desk_query.get(desk_id)
```

The method returns the requested `Desk` or raises `DeskNotFoundError`.

Avoid:

```python
desk = desk_service.create(command)

if desk is None:
    ...
```

Avoid:

```python
success = desk_service.update(command)

if not success:
    ...
```

Predicate query methods may return booleans where the boolean itself is the requested value.

For example:

```python
exists = desk_query.exists(desk_id)
```

This is not a success flag. It is an explicit existence query whose domain result is either `True` or `False`.

Optional lookup methods may return `None` only where absence is an expected, documented result and the method name makes that contract explicit.

For example:

```python
desk = desk_query.find_by_code(code)
```

By convention:

* `get_*` methods return a value or raise a not-found exception;
* `find_*` methods may return `None`;
* `exists` methods return `bool`;
* mutation methods return the affected domain object or structured result.

Callers must not inspect exception message text to determine behaviour. They should catch the documented domain-specific exception class.


# Dependency injection

Services should receive their dependencies explicitly where practical.

Preferred:

```python
class FileManager:
    def __init__(
        self,
        provider: FileProvider,
        audit_service: AuditService,
    ) -> None:
        self.provider = provider
        self.audit_service = audit_service
```

This makes services easier to test and prevents hidden infrastructure dependencies.

Flask composition helpers may create configured service instances:

```python
def get_file_manager() -> FileManager:
    if "file_manager" not in g:
        g.file_manager = FileManager(
            provider=get_file_provider(),
            audit_service=get_audit_service(),
        )

    return g.file_manager
```

Business modules should request the public service rather than instantiate infrastructure providers.

# Flask context dependencies

A service may read application configuration through a composition factory, but the service itself should not depend unnecessarily on:

* `request`;
* `session`;
* `current_user`;
* route parameters;
* template globals.

Preferred:

```python
service.assign(
    person_id=person_id,
    assigned_by_id=current_user.id,
)
```

Avoid:

```python
service.assign_from_current_request()
```

Explicit inputs make the service usable from:

* routes;
* CLI commands;
* Celery tasks;
* tests;
* future API endpoints.

# Transaction ownership

A service performing a business workflow should normally own the transaction.

A public mutation method should clearly use one of these patterns:

## Commit-owning service

The service commits or rolls back the transaction.

```python
def create_type(...) -> FileType:
    record = FileType(...)
    db.session.add(record)

    try:
        db.session.commit()
    except SQLAlchemyError as exc:
        db.session.rollback()
        raise FileTypePersistenceError(...) from exc

    return record
```

This is suitable for self-contained application workflows.

## Caller-owned unit of work

The service flushes but does not commit because it is designed to participate in a larger workflow.

This behaviour must be explicit in naming or documentation.

```python
def add_evidence_without_commit(...) -> EvidenceRecord:
    ...
    db.session.flush()
    return record
```

Caller-owned transactions should be used sparingly because they expose more internal assumptions.

## Default rule

Unless a service explicitly documents otherwise, callers should assume a public mutation method owns its transaction.

Routes should not call an ordinary service method and then issue an additional commit for the same workflow.

# One commit per workflow

Avoid workflows that commit repeatedly between dependent operations.

Avoid:

```python
record = CompetencyRecord(...)
db.session.add(record)
db.session.commit()

evidence = Evidence(...)
db.session.add(evidence)
db.session.commit()
```

Prefer:

```python
record = competency_service.assign_with_evidence(...)
```

with one database transaction.

Multiple commits make compensation, rollback and testing more difficult.

# External systems and compensation

PostgreSQL and S3 cannot share one transaction.

Where a workflow crosses such boundaries, the service must define compensation behaviour.

The file upload workflow follows this pattern:

1. validate and prepare the stream;
2. upload the immutable object;
3. create the database record;
4. commit the database transaction;
5. if the commit fails, attempt to remove the uploaded object;
6. log any orphan requiring reconciliation.

Compensation cannot guarantee perfect atomicity, but it should reduce inconsistent state and make failures observable.

Services that perform external side effects must document:

* operation order;
* compensation behaviour;
* possible reconciliation requirements;
* idempotency assumptions.

# Flush before external side effects

When a database-generated value is required before an external action, use `flush()` rather than committing prematurely.

Example:

```python
record = SomeRecord(...)
db.session.add(record)
db.session.flush()

external_service.perform(record.id)
```

The final commit still belongs to the overall workflow.

# Application exceptions

Services must raise exceptions meaningful to callers.

Example hierarchy:

```python
class CatalogueError(Exception):
    pass


class CatalogueRecordNotFoundError(CatalogueError):
    pass


class DuplicateCatalogueCodeError(CatalogueError):
    pass


class CataloguePersistenceError(CatalogueError):
    pass
```

Routes should handle these instead of raw SQLAlchemy or provider exceptions.

Third-party exceptions should usually be chained:

```python
except SQLAlchemyError as exc:
    db.session.rollback()
    raise CataloguePersistenceError(
        "The catalogue record could not be saved."
    ) from exc
```

# Exception messages

Exception messages should:

* describe the application-level failure;
* avoid exposing credentials or sensitive internals;
* be suitable for logs;
* not assume they will be displayed directly to users.

User-facing messages should normally be selected by the route or UI layer.

# Exception granularity

Use enough exception types to allow meaningful caller behaviour.

For example:

```python
ManagedFileNotFoundError
DeletedFileError
FileTooLargeError
FilePersistenceError
```

Avoid creating a unique exception for every individual validation sentence.

A useful exception changes how the caller responds.

# Query methods

Where absence represents failure of the requested operation, the query must raise a domain-specific not-found exception.

Methods prefixed with `get_` must return the requested value or raise a not-found exception.

Methods prefixed with `find_` may return `None` where absence is an expected and documented result.

Predicate methods such as `exists` may return `bool` because the boolean is the requested domain value.

The contract must be clear from the method name, type annotation and documentation.


# Stable identifiers

Service methods should generally accept stable identifiers such as UUIDs and stable catalogue codes.

Examples:

```python
get_file(file_id)
get_type_by_code("profile_photo")
```

Avoid using editable display names as service identifiers.

# Model return values

Services may return SQLAlchemy model instances where the service and caller operate within the same application process and session.

For more complex workflows, structured result dataclasses may be preferable.

Example:

```python
@dataclass(frozen=True)
class UploadResult:
    file_object: FileObject
    thumbnail_scheduled: bool
    scan_scheduled: bool
```

Do not return raw third-party response dictionaries as the public result of a domain service.

# Validation layers

Response Connect uses several validation layers.

## Request validation

Forms and request parsers validate:

* field presence;
* basic formatting;
* HTTP input structure.

## Service validation

Services enforce:

* business rules;
* record state;
* catalogue rules;
* permissions when appropriate;
* cross-record invariants.

## Database constraints

The database enforces:

* uniqueness;
* non-null requirements;
* foreign keys;
* check constraints;
* structural integrity.

No one layer replaces the others.

A service must remain safe when called outside a form submission.

# Permission checks

HTTP routes should enforce user-facing permissions before calling sensitive services.

Services that may be invoked from several contexts should also support explicit authorisation or scope validation where the rule is part of the business workflow.

Avoid hidden dependence on `current_user`.

Preferred:

```python
service.approve(
    document_id=document_id,
    approved_by_id=current_user.id,
)
```

A future policy or authorisation service may centralise more complex scope decisions.

# Audit integration

A service should create audit events only after it knows the relevant operation succeeded.

For database-only operations, audit records should normally participate in the same transaction.

For external side effects, the audit semantics must distinguish between:

* requested;
* completed;
* failed;
* compensated;
* reconciliation required.

Audit logging must not silently turn a successful business operation into a failed one unless the audit record is legally or operationally essential to the transaction.

That decision should be explicit for each capability.

# Service-to-service calls

Services may call other public services.

Example:

```python
file_object = file_manager.create_from_filestorage(...)
competency = competency_service.attach_evidence(
    competency_id=competency_id,
    file_id=file_object.id,
)
```

For workflows that must coordinate several capabilities atomically or compensate across systems, introduce a higher-level application service rather than placing orchestration in the route.

Example:

```python
MandatoryTrainingWorkflowService
```

This service may coordinate:

* competencies;
* files;
* audit;
* notifications.

# Avoid cross-module private imports

A service should not import another module's private helper or provider.

Preferred:

```python
from app.files import get_file_manager
```

Avoid:

```python
from app.files.providers.s3 import S3FileProvider
from app.files.manager import _normalise_content_type
```

# Idempotency

Service methods used by asynchronous tasks should support repeated execution safely.

Possible strategies include:

* checking whether the desired result already exists;
* using unique constraints;
* recording an idempotency key;
* using stable output object keys;
* checking current lifecycle state;
* locking the relevant row where necessary.

Example:

```python
def generate_thumbnail(file_id: UUID) -> FileDerivative:
    existing = self.get_existing_thumbnail(file_id)

    if existing is not None:
        return existing

    ...
```

Idempotency should be enforced by data and service logic, not assumed from task-delivery behaviour.

# Concurrency

Where two users or workers may update the same record, services should consider:

* optimistic checks;
* unique constraints;
* row locking;
* state transition validation;
* retry behaviour.

A service must not assume that a prior page load still reflects the current database state.

State transitions should be checked at the moment of mutation.

# State transitions

Lifecycle changes should use explicit service methods.

Preferred:

```python
document_service.approve(...)
document_service.publish(...)
document_service.supersede(...)
```

Avoid generic mutation such as:

```python
document.status = request.form["status"]
```

Explicit methods make permissions, validation, audit and notifications easier to apply consistently.

# Soft deletion

Where records require auditability or recovery, deletion should normally be a lifecycle transition.

Example:

```python
file_manager.soft_delete(file_object)
file_manager.restore(file_object)
```

Permanent purge should be a separate privileged operation.

Services should define whether related records:

* remain visible;
* are hidden from ordinary queries;
* block restoration;
* are cascaded;
* require retention checks.

# Logging

Services should log operationally useful failures and exceptional states.

Logs should include stable identifiers where available:

```python
logger.exception(
    "Failed to purge file object %s",
    file_object.id,
)
```

Logs must not include:

* secrets;
* passwords;
* access tokens;
* unnecessary patient data;
* full file contents;
* sensitive form payloads.

Expected validation errors generally do not require exception-level logging.

# Service factories

Application composition functions should live close to the owning capability.

Example:

```python
def get_catalogue_service() -> CatalogueService:
    if "catalogue_service" not in g:
        g.catalogue_service = CatalogueService(
            audit_service=get_audit_service(),
        )

    return g.catalogue_service
```

Factories should:

* configure dependencies;
* reuse instances within the Flask context;
* hide provider-specific construction;
* avoid performing business actions.

# Testing services

Service tests should cover public behaviour.

Typical cases include:

* successful creation or mutation;
* validation failure;
* duplicate stable code;
* missing record;
* inactive record behaviour;
* transaction rollback;
* compensation after external failure;
* idempotent repeated calls;
* significant state transitions;
* audit integration;
* permission or scope enforcement where applicable.

Tests should mock or replace infrastructure at the service boundary rather than mocking internal helper functions excessively.

# Test doubles

Provider interfaces should be replaceable with fakes.

Example:

```python
class FakeFileProvider:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    def upload_fileobj(...):
        ...

    def delete_object(...):
        ...
```

A fake often provides more useful behavioural testing than a large number of brittle mocks.

Integration tests should still exercise the real provider where appropriate.

# Method size and decomposition

A public service method should describe one coherent workflow.

If it becomes difficult to understand, split private steps by responsibility:

```python
def create_file(...):
    prepared = self._prepare_upload(...)
    object_key = self._build_object_key(...)
    self._upload(...)
    return self._persist_record(...)
```

Private decomposition should clarify the workflow rather than hide business behaviour across many tiny methods.

# Dataclasses and value objects

Use dataclasses or value objects when a group of values forms a meaningful concept.

Examples:

```python
@dataclass(frozen=True)
class PreparedUpload:
    stream: BinaryIO
    size_bytes: int
    sha256: str
    original_filename: str
    mime_type: str
```

This is preferable to passing long unstructured tuples through several methods.

# Catalogue service expectations

The future catalogue framework should provide shared service behaviour for:

* retrieving by stable code;
* listing active records;
* creating custom records;
* updating editable display fields;
* activating and deactivating;
* protecting system codes;
* sort ordering;
* duplicate detection;
* reference-data synchronisation.

Catalogue-specific modules should extend or configure the shared behaviour rather than duplicate it.

# Service documentation

Public service classes and methods should document:

* owned responsibility;
* transaction behaviour;
* significant side effects;
* exceptions;
* return values;
* idempotency where relevant.

Comments should explain why a non-obvious decision exists rather than repeat the code.

# Architecture decision: service-owned workflows

## Decision

Response Connect will implement significant application and domain workflows through explicit service interfaces.

Routes, tasks and CLI commands will remain thin adapters around those services.

## Context

Business logic placed directly in routes or tasks becomes difficult to reuse, test and coordinate. Direct model manipulation across modules also weakens ownership boundaries.

The application requires consistent handling of transactions, external systems, audit events and exceptions.

## Alternatives considered

### Route-driven workflows

This is straightforward for small pages but creates duplicated logic and HTTP-dependent business behaviour.

### Active Record models with large behaviour methods

This can keep behaviour near data, but external services, multi-record workflows and cross-capability coordination make models overly coupled.

### Generic repository layer for every model

A repository abstraction could hide SQLAlchemy but would add indirection without necessarily expressing business intent.

## Consequences

Benefits:

* reusable workflows;
* clearer module ownership;
* easier service-level testing;
* consistent transactions and exceptions;
* thinner routes and tasks;
* better provider isolation.

Trade-offs:

* more explicit classes and interfaces;
* dependency composition must be managed;
* simple CRUD operations may require slightly more structure;
* contributors must resist bypassing services for convenience.

# Service review checklist

Before approving a new service or public method, confirm:

1. Does the service own a clear capability?
2. Is the method named for business intent?
3. Are dependencies explicit?
4. Is transaction ownership clear?
5. Are external side effects ordered safely?
6. Is compensation defined where required?
7. Are application exceptions raised?
8. Are stable identifiers used?
9. Is repeated asynchronous execution safe?
10. Are significant actions audited?
11. Can the behaviour be tested without HTTP?
12. Is another module's private implementation being accessed?

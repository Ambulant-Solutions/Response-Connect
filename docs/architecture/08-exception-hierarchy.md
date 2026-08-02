# Error Handling Architecture

## Purpose

This chapter defines how Response Connect represents, raises, translates, logs and presents errors.

It establishes:

* the platform exception hierarchy;
* the difference between expected business failures and unexpected system failures;
* where exceptions should be raised and caught;
* how services protect callers from infrastructure-specific exceptions;
* how transactions should behave when errors occur;
* how HTTP, HTMX, API and worker processes should present failures;
* how platform logging and the future Event Journal relate to errors;
* the conventions that every module must follow.

The goal is not to create a large or complicated inheritance tree.

The goal is to ensure that every error has clear meaning, clear ownership and predictable handling.

---

# Guiding principle

> Exceptions should describe application meaning, not implementation detail.

Callers should receive errors that explain what failed in the Response Connect domain.

They should not need to understand:

* SQLAlchemy;
* PostgreSQL;
* boto3;
* botocore;
* MinIO;
* Redis;
* Celery;
* SMTP;
* HTTP client libraries;
* provider-specific SDKs.

Provider and persistence errors must be translated before they cross a module boundary.

---

# Error handling objectives

Response Connect error handling should:

1. preserve clear business meaning;
2. prevent infrastructure exceptions leaking into routes and business modules;
3. support consistent HTTP and HTMX responses;
4. support structured API error responses;
5. preserve correct database rollback behaviour;
6. distinguish expected outcomes from unexpected failures;
7. avoid unnecessary logging of normal validation problems;
8. support future Event Journal and security-event integration;
9. remain easy for contributors to understand;
10. avoid large exception hierarchies with little practical value.

---

# Error categories

Response Connect recognises several broad error categories.

## Validation errors

Validation errors mean supplied data is invalid.

Examples:

* a required name is missing;
* an end date occurs before a start date;
* an invalid file extension is supplied;
* a stable code uses an invalid format;
* a file exceeds an allowed size;
* a lifecycle transition lacks required information.

Validation errors are expected application behaviour.

They normally result in:

* inline form errors;
* an HTTP `400` response for APIs;
* no exception-level platform log;
* no persistent audit event unless the invalid attempt is security-relevant.

## Not-found errors

Not-found errors mean a requested domain record does not exist or is not available to the caller.

Examples:

* a file-processing policy ID does not exist;
* a Desk cannot be found;
* a Clinical Grade code is unknown;
* a referenced file has been purged;
* a lifecycle assignment does not exist.

A not-found result may represent:

* a genuinely missing record;
* a record outside the caller’s authorised scope;
* a record that has been removed or archived.

Routes must avoid revealing the existence of records that the caller is not authorised to view.

## Conflict errors

Conflict errors mean a valid request cannot be completed because it conflicts with existing state.

Examples:

* a duplicate stable code;
* a duplicate catalogue name;
* an overlapping assignment;
* a Desk hierarchy cycle;
* a record cannot be deactivated while currently in use;
* a system-owned record conflicts with a custom record;
* a document cannot be published from its current state.

Conflicts are expected business outcomes.

They normally result in:

* a form-level or field-level error;
* an HTTP `409` response for APIs;
* no exception-level platform log.

## Permission errors

Permission errors mean an authenticated actor is not authorised to perform an action.

Examples:

* a user lacks `hr:configure`;
* a user has a permission but not the required Desk scope;
* a user cannot access a restricted Event Journal entry;
* a user cannot approve their own controlled document;
* a user cannot purge files.

Permission failures may later create security events where appropriate.

They should not expose sensitive record details.

## Lifecycle errors

Lifecycle errors mean a requested state transition is not valid.

Examples:

* activating an already archived record;
* closing a Desk before required checks are complete;
* assigning a Clinical Grade during an overlapping period;
* completing an assignment without an end date;
* restoring a permanently purged file;
* publishing a superseded document.

Lifecycle errors are a specialised form of business-rule failure.

They may also be represented as validation or conflict errors when that gives the caller clearer handling.

## Persistence errors

Persistence errors mean Response Connect could not store or retrieve application state reliably.

Examples:

* a database transaction fails;
* an integrity constraint is violated unexpectedly;
* a commit cannot complete;
* a rollback fails;
* a required stored record cannot be refreshed.

Persistence errors are not normal user validation outcomes.

They should normally be logged.

## Infrastructure errors

Infrastructure errors mean an external or technical dependency failed.

Examples:

* S3-compatible storage is unavailable;
* Redis cannot be reached;
* Celery cannot enqueue a task;
* an email provider rejects a connection;
* malware scanning is unavailable;
* an external API times out;
* a file cannot be read from object storage.

Infrastructure errors should hide provider-specific exception details from business callers.

They should normally be logged with structured context.

## Configuration errors

Configuration errors mean the application cannot safely operate because required configuration is missing or invalid.

Examples:

* no S3 bucket is configured;
* an invalid storage provider is selected;
* a required encryption key is missing;
* mutually exclusive settings are enabled;
* a service is registered twice;
* a required platform registry was not initialised.

Configuration errors normally indicate an installation or deployment problem rather than bad user input.

They should be logged clearly and should normally prevent the affected operation from continuing.

## Unexpected errors

Unexpected errors are defects or unclassified failures that were not anticipated by the application.

Examples:

* programming errors;
* invalid assumptions;
* unexpected third-party behaviour;
* uncaught type errors;
* incorrect state not covered by existing validation.

Unexpected errors should:

* propagate to a global error boundary;
* be logged with traceback information;
* return a generic user-facing response;
* avoid exposing internal details;
* be investigated and, where appropriate, translated into a defined platform exception later.

---

# Platform exception hierarchy

Create a small shared hierarchy under:

```text
app/exceptions.py
```

The intended hierarchy is:

```text
ResponseConnectError
├── ValidationError
├── NotFoundError
├── ConflictError
├── PermissionDeniedError
├── LifecycleError
├── PersistenceError
├── InfrastructureError
└── ConfigurationError
```

The base classes provide consistent categories across the platform.

Modules may define more specific exceptions where they improve clarity.

Example:

```text
ResponseConnectError
└── ConflictError
    └── FileProcessingPolicyConflictError
```

Another example:

```text
ResponseConnectError
└── NotFoundError
    └── FileProcessingPolicyNotFoundError
```

The hierarchy should remain shallow.

Deep inheritance trees are discouraged.

---

# Base exception classes

The platform base exceptions should initially remain simple.

Example:

```python
class ResponseConnectError(Exception):
    """Base class for expected Response Connect errors."""


class ValidationError(ResponseConnectError):
    """Raised when supplied application data is invalid."""


class NotFoundError(ResponseConnectError):
    """Raised when a requested domain record cannot be found."""


class ConflictError(ResponseConnectError):
    """Raised when a request conflicts with existing state."""


class PermissionDeniedError(ResponseConnectError):
    """Raised when an actor is not authorised to perform an action."""


class LifecycleError(ResponseConnectError):
    """Raised when a requested lifecycle transition is invalid."""


class PersistenceError(ResponseConnectError):
    """Raised when application state cannot be persisted reliably."""


class InfrastructureError(ResponseConnectError):
    """Raised when an external technical dependency fails."""


class ConfigurationError(ResponseConnectError):
    """Raised when required application configuration is invalid."""
```

Structured fields may be introduced later if concrete use cases justify them.

Do not add attributes merely because they may be useful eventually.

---

# Module-specific exception hierarchies

Each platform or business module may define a module-specific base exception.

Example:

```python
class FileProcessingPolicyError(ResponseConnectError):
    """Base error for file-processing policy operations."""
```

Specific exceptions should then derive from both the module meaning and the platform category where practical.

Example:

```python
class FileProcessingPolicyNotFoundError(
    FileProcessingPolicyError,
    NotFoundError,
):
    """Raised when a file-processing policy cannot be found."""
```

Example:

```python
class FileProcessingPolicyCodeConflictError(
    FileProcessingPolicyError,
    ConflictError,
):
    """Raised when a file-processing policy code is already used."""
```

Example:

```python
class InvalidFileProcessingPolicyError(
    FileProcessingPolicyError,
    ValidationError,
):
    """Raised when file-processing policy input is invalid."""
```

This allows callers to catch either:

```python
except FileProcessingPolicyError:
```

or the broader category:

```python
except ConflictError:
```

Multiple inheritance should be limited to this module-category pattern.

Avoid complicated inheritance graphs.

---

# Naming conventions

Custom exception names must end with:

```text
Error
```

Good names include:

```text
FileProcessingPolicyNotFoundError
ReferenceDataConflictError
InvalidCatalogueCodeError
DeskHierarchyCycleError
ClinicalGradeAssignmentOverlapError
StorageProviderUnavailableError
```

Avoid vague names such as:

```text
DuplicateError
InvalidError
DatabaseProblem
OperationFailed
GeneralException
```

Exception names should answer:

* what concept failed;
* what kind of failure occurred.

---

# Business meaning over implementation

Services should translate implementation-specific errors.

Bad:

```python
raise IntegrityError(...)
```

Bad:

```python
raise ClientError(...)
```

Bad:

```python
raise SQLAlchemyError(...)
```

Good:

```python
raise FileProcessingPolicyCodeConflictError(
    "A file-processing policy already uses this code."
)
```

Good:

```python
raise FileStorageUnavailableError(
    "The file could not be stored."
)
```

Good:

```python
raise ReferenceDataSynchronisationError(
    "Reference data could not be synchronised."
)
```

Provider-specific exceptions may be retained as the Python exception cause:

```python
raise FileStorageUnavailableError(
    "The file could not be stored."
) from exc
```

This preserves diagnostic information without leaking provider details to callers.

---

# Raising exceptions

Exceptions should be raised at the layer that understands their meaning.

## Validators

Validators raise validation-focused exceptions.

Example:

```python
if start_date > end_date:
    raise ValidationError(
        "The start date cannot be after the end date."
    )
```

Validators should not:

* commit transactions;
* log expected validation failures;
* render responses;
* access Flask request state unless specifically designed as an HTTP validator.

## Services

Services raise domain and platform exceptions.

They should:

* validate commands;
* enforce business rules;
* translate infrastructure failures;
* translate persistence failures;
* own rollback behaviour;
* provide meaningful exception messages.

## Models

Models should rely primarily on:

* database constraints;
* simple invariant helpers;
* properties.

Models should not generally raise route-oriented or presentation-oriented exceptions.

Business workflows belong in services.

## Routes

Routes should rarely originate domain exceptions.

They should:

* parse request input;
* construct commands;
* call services;
* catch expected application exceptions when they can render a useful response.

## Infrastructure adapters

Infrastructure adapters should translate provider-specific failures into platform infrastructure exceptions.

Example:

```text
botocore ClientError
        ↓
S3FileProvider
        ↓
FileStorageError
```

The Files service should not require callers to import `botocore`.

---

# Catching exceptions

> Catch an exception only when the current layer can add value.

Valid reasons to catch an exception include:

* translating it into a domain exception;
* rolling back a transaction;
* adding structured operational context to a log;
* rendering a useful form response;
* returning a structured API response;
* applying a documented retry policy;
* performing compensation.

Avoid broad catches such as:

```python
except Exception:
```

unless they occur at a genuine global boundary such as:

* the Flask application error handler;
* a Celery task boundary;
* a CLI command boundary;
* an integration runner.

Even at global boundaries, unexpected exceptions should normally be re-raised or reported after appropriate handling.

---

# Transaction behaviour

Services own transaction boundaries for coherent workflows.

A typical service operation should:

1. validate the command;
2. load required records;
3. enforce business rules;
4. prepare state changes;
5. prepare Event Journal entries where required;
6. commit once;
7. return the result.

When persistence fails:

```python
try:
    session.commit()
except SQLAlchemyError as exc:
    session.rollback()
    raise PersistenceError(
        "The operation could not be saved."
    ) from exc
```

A service must not leave the SQLAlchemy session in a failed transaction state.

Expected business validation should normally occur before persistence.

Database constraints remain necessary as the final line of protection.

---

# Integrity errors

An integrity error may represent either:

* an expected business conflict;
* an unexpected persistence failure.

Services should inspect known constraints where this improves meaning.

Example:

```python
if constraint_name == "uq_file_processing_policies_code":
    raise FileProcessingPolicyCodeConflictError(
        "A file-processing policy with that code already exists."
    ) from exc
```

Unknown integrity errors should become a persistence error:

```python
raise FileProcessingPolicyPersistenceError(
    "The file-processing policy could not be saved."
) from exc
```

Do not expose raw constraint names to users.

---

# Error messages

Exception messages should be:

* understandable;
* specific enough to be useful;
* free from secrets;
* free from SQL or provider details;
* appropriate for logs or user-facing translation;
* stable enough for humans, but not treated as machine identifiers.

Machine logic must use exception classes or explicit error codes, not compare message text.

Bad:

```python
if str(exc) == "duplicate":
```

Good:

```python
except FileProcessingPolicyCodeConflictError:
```

---

# Structured exception context

Some future exceptions may require structured context.

Examples include:

* conflicting record ID;
* stable code;
* field name;
* lifecycle state;
* retryability;
* provider operation.

Where structured context is needed, prefer explicit attributes.

Example:

```python
class AssignmentOverlapError(ConflictError):
    def __init__(
        self,
        message: str,
        *,
        conflicting_assignment_id: UUID,
    ) -> None:
        super().__init__(message)
        self.conflicting_assignment_id = (
            conflicting_assignment_id
        )
```

Do not attach whole model instances to exceptions.

Do not attach sensitive patient or staff data unless strictly necessary.

---

# Logging rules

Platform logging and exceptions are related but distinct.

An exception does not automatically require a log entry.

## Do not normally log

Expected application outcomes should normally not produce exception logs:

* invalid form input;
* duplicate names;
* duplicate stable codes;
* inactive records;
* ordinary lifecycle conflicts;
* missing optional records;
* user-correctable validation errors.

Logging these at error level creates noise and hides real failures.

## Log at warning level where appropriate

Warnings may be appropriate for:

* repeated permission denials;
* recoverable integration failures;
* reference-data conflicts;
* temporary provider unavailability;
* rejected background jobs;
* suspicious but non-fatal activity.

## Log at error or exception level

Error or exception logging is appropriate for:

* database failures;
* object-storage failures;
* Redis or Celery failures;
* unexpected provider responses;
* failed compensation;
* configuration failures;
* unexpected exceptions;
* data-integrity conditions that should not occur.

Use structured platform events.

Example:

```python
log_platform_event(
    logger,
    "files.storage_failed",
    level=logging.ERROR,
    fields={
        "operation": "upload",
        "provider": "s3",
    },
)
```

Do not log:

* passwords;
* access tokens;
* secret keys;
* complete patient records;
* file contents;
* unnecessary personal data.

---

# Tracebacks

Tracebacks are useful for unexpected failures.

Use:

```python
logger.exception(
    "Unexpected file-storage failure."
)
```

inside an active exception handler when the traceback is needed.

Expected validation and conflict errors should not normally generate tracebacks.

---

# Flask route handling

Routes should convert expected exceptions into suitable user-facing responses.

Example:

```python
try:
    policy = service.create(command)
except InvalidFileProcessingPolicyError as exc:
    form.form_errors.append(str(exc))
    return render_template(
        "files/policies/form.html",
        form=form,
    ), 400
```

A route may catch a specific module exception or a platform category.

Specific exceptions are preferable where the UI can provide targeted feedback.

Broad platform-category catches are useful for shared handlers.

Routes should not catch persistence or infrastructure errors merely to hide them.

Those errors should normally reach a central handler after being logged or translated by the service.

---

# Global Flask error handlers

The Flask application should eventually register global handlers for platform exception categories.

Suggested behaviour:

| Exception category      | HTML response                   | API status |
| ----------------------- | ------------------------------- | ---------: |
| `ValidationError`       | Render form or bad-request page |        400 |
| `PermissionDeniedError` | Access-denied page or redirect  |        403 |
| `NotFoundError`         | Not-found page                  |        404 |
| `ConflictError`         | Conflict message or form        |        409 |
| `LifecycleError`        | Conflict message                |        409 |
| `PersistenceError`      | Generic service-failure page    |        500 |
| `InfrastructureError`   | Temporary service-failure page  |        503 |
| `ConfigurationError`    | Generic system-error page       |        500 |

Do not expose exception causes or tracebacks to end users.

---

# HTMX responses

HTMX endpoints should return useful partial responses.

## Validation failure

Return:

* the form partial;
* field errors;
* form-level errors;
* an appropriate `400` status where helpful.

## Conflict

Return:

* the affected form or action panel;
* a clear conflict message;
* normally a `409` status.

## Permission denied

Return:

* a suitable access-denied partial;
* or an `HX-Redirect` to an authorised page;
* normally a `403` status.

## Infrastructure failure

Return:

* a generic retryable error component;
* no provider details;
* normally a `503` status where the failure is temporary.

HTMX-specific presentation belongs in routes or shared HTTP handlers, not in service exceptions.

---

# API responses

API errors should use a stable response structure.

Example:

```json
{
  "error": {
    "code": "files.processing_policy_conflict",
    "message": "A file-processing policy already uses this code.",
    "fields": {
      "code": [
        "This code is already in use."
      ]
    }
  }
}
```

The API error code is separate from:

* the Python exception class name;
* the human-readable message;
* the Event Journal event code.

API error codes should be stable and documented.

Suggested status mapping:

```text
ValidationError          400
PermissionDeniedError    403
NotFoundError            404
ConflictError            409
LifecycleError           409
InfrastructureError      503
PersistenceError         500
ConfigurationError       500
```

---

# CLI handling

CLI commands are global error boundaries.

They should:

* catch expected platform exceptions;
* print concise error messages;
* return a non-zero exit status;
* avoid raw tracebacks for expected errors;
* allow unexpected errors to produce diagnostic information in development.

Example:

```python
try:
    result = synchroniser.synchronise()
except ReferenceDataConflictError as exc:
    raise click.ClickException(str(exc)) from exc
```

CLI commands should not duplicate service validation.

---

# Background worker handling

Celery tasks are global execution boundaries.

Tasks should distinguish:

* retryable infrastructure failures;
* permanent validation failures;
* business conflicts;
* unexpected errors.

## Retryable failures

Examples:

* temporary SMTP failure;
* temporary S3 outage;
* external API timeout.

These may be retried according to a bounded retry policy.

## Non-retryable failures

Examples:

* invalid command data;
* missing required record;
* unsupported lifecycle transition;
* permanent permission or configuration conflict.

These should not be retried indefinitely.

Task logs should include:

* task type;
* correlation ID;
* attempt number;
* retryability;
* relevant non-sensitive identifiers.

The future Event Journal may record persistent task outcomes when operationally or administratively significant.

---

# Provider failure translation

Every provider adapter should define its translation boundary.

Examples:

## S3-compatible storage

```text
botocore exception
        ↓
S3 provider
        ↓
FileStorageError
```

## Redis

```text
redis exception
        ↓
queue or cache adapter
        ↓
QueueInfrastructureError
```

## SMTP

```text
SMTP exception
        ↓
mail provider
        ↓
NotificationDeliveryError
```

## External HTTP APIs

```text
HTTP client exception
        ↓
integration adapter
        ↓
IntegrationUnavailableError
```

Business services should not contain provider-specific exception branches unless they own the adapter.

---

# Compensation errors

Some workflows span PostgreSQL and external infrastructure and cannot be committed atomically.

Example:

```text
Upload object to S3
        ↓
Create database record
        ↓
Database commit fails
        ↓
Delete uploaded object
```

If compensation also fails, the service should raise a specific infrastructure or persistence exception and log the orphaned state.

Example:

```text
FileUploadCompensationError
```

The roadmap must capture reconciliation tooling for such cases.

Do not suppress failed compensation.

---

# Event Journal integration

The Event Journal is not yet implemented.

When it exists, exceptions should not automatically create journal events.

The Event Journal records significant business and operational facts.

Examples that may create events:

* permission denied for a sensitive operation;
* repeated authentication failure;
* malware detected;
* document publication failed after approval;
* operational dispatch rejected;
* external integration import failed;
* compensation failure leaving reconciliation work.

Examples that normally should not create events:

* ordinary form validation failure;
* duplicate display name;
* missing optional input;
* typo in a catalogue code;
* normal not-found response.

Event recording decisions belong to the owning service or global security boundary.

---

# Security errors

Security-related failures require particular care.

Examples:

* authentication failure;
* account lockout;
* access denied;
* session revocation;
* permission escalation attempt;
* invalid security token;
* CSRF failure.

Security errors may require:

* a generic user-facing message;
* structured platform logging;
* a future security Event Journal entry;
* rate limiting;
* alerting;
* redaction of sensitive details.

Do not reveal whether a particular account, patient, incident or record exists unless authorised.

---

# Forms and field errors

Field validation should remain attached to form fields where possible.

Example:

```python
form.code.errors.append(
    "This code is already in use."
)
```

Service exceptions may be translated into field errors by routes.

The service should not depend on WTForms.

This keeps services usable from:

* routes;
* APIs;
* CLI commands;
* workers;
* tests.

---

# User-facing wording

User-facing errors should:

* explain what could not be completed;
* identify corrective action where possible;
* avoid blame;
* avoid technical implementation details;
* avoid ambiguous messages such as “Something went wrong” for expected conflicts.

Good:

```text
This job position cannot be deactivated while it has current or future staff assignments.
```

Good:

```text
The file could not be stored because the storage service is temporarily unavailable. Try again later.
```

Bad:

```text
IntegrityError on uq_job_positions_name.
```

Bad:

```text
Botocore ClientError: AccessDenied.
```

---

# Module conventions

Each module that defines custom exceptions should use:

```text
exceptions.py
```

Example:

```text
app/files/exceptions.py
app/reference_data/exceptions.py
app/events/exceptions.py
app/lifecycle/exceptions.py
app/desks/exceptions.py
```

The module should expose intentionally public exceptions through its package `__init__.py` where external callers are expected to catch them.

Internal provider exceptions may remain private.

---

# Public exception exports

Only exceptions that callers are expected to handle should be public.

Example:

```python
__all__ = [
    "FileNotFoundError",
    "FilePersistenceError",
    "FileStorageError",
]
```

Provider-specific or internal helper exceptions should not be exported merely because they exist.

Public API architecture tests should validate exception exports.

---

# Testing requirements

Every custom exception hierarchy should be tested.

## Unit tests

Test:

* inheritance;
* messages;
* structured attributes where present;
* translation from provider exceptions;
* rollback behaviour.

## Service tests

Test that services raise the intended domain exception for:

* invalid input;
* missing records;
* duplicate values;
* invalid lifecycle transitions;
* persistence failures;
* infrastructure failures.

## Route tests

Test that routes convert exceptions into:

* appropriate status codes;
* correct templates or partials;
* useful form errors;
* safe messages.

## Architecture tests

Architecture fitness tests should eventually enforce:

* every public custom exception derives from `ResponseConnectError`;
* exception names end in `Error`;
* platform exceptions do not import routes;
* platform exceptions do not depend on templates;
* module exception exports resolve;
* provider-specific exceptions do not escape public service tests.

---

# Current exception review

The current codebase includes module-specific hierarchies for:

* Catalogues;
* Files;
* File Processing Policies;
* Reference Data.

These currently derive directly from `Exception` in several places.

They should be reviewed and migrated onto the shared platform categories in a controlled refactor.

The refactor must preserve existing public names where practical.

Renaming public exceptions requires:

* caller updates;
* tests;
* documentation;
* a compatibility decision where necessary.

---

# Initial refactor targets

The first refactor should introduce:

```text
app/exceptions.py
```

Then align:

```text
app/catalogues/exceptions.py
app/files/exceptions.py
app/reference_data/exceptions.py
```

Suggested mappings include:

| Existing concept                       | Platform category                           |
| -------------------------------------- | ------------------------------------------- |
| Invalid catalogue code                 | `ValidationError`                           |
| Catalogue record missing               | `NotFoundError`                             |
| Duplicate catalogue code               | `ConflictError`                             |
| Protected system record                | `ConflictError` or `LifecycleError`         |
| Processing policy missing              | `NotFoundError`                             |
| Processing policy duplicate            | `ConflictError`                             |
| Invalid processing policy              | `ValidationError`                           |
| Processing policy persistence failure  | `PersistenceError`                          |
| Reference dataset missing              | `NotFoundError`                             |
| Duplicate dataset registration         | `ConfigurationError`                        |
| Reference-data conflict                | `ConflictError`                             |
| Reference-data synchronisation failure | `PersistenceError` or `InfrastructureError` |

The exact mapping should be confirmed during implementation review.

---

# Non-goals

This architecture does not require:

* one exception class per possible message;
* deep inheritance trees;
* provider-specific errors in business modules;
* exception-driven normal branching where a return value is clearer;
* automatic Event Journal entries for every exception;
* automatic logging of every exception;
* exposing internal errors through HTTP;
* replacing database constraints with Python validation.

---

# Decision summary

Response Connect will use a small shared platform exception hierarchy.

Module-specific exceptions will preserve domain meaning while deriving from common platform categories.

Services will translate persistence and provider exceptions before they escape module boundaries.

Expected validation and conflict errors will be treated as normal application behaviour and will not normally be logged at exception level.

Routes, APIs, CLI commands and workers will translate platform exceptions at their respective execution boundaries.

Platform logging will record technical failures.

The future Event Journal will record only significant operational, audit, system and security events rather than every application exception.

---

# Implementation checklist

Before marking the exception-hierarchy work complete:

* [ ] Add `app/exceptions.py`.
* [ ] Add shared platform base exceptions.
* [ ] Inventory existing custom exceptions.
* [ ] Map existing exceptions to platform categories.
* [ ] Refactor Catalogue exceptions.
* [ ] Refactor Files exceptions.
* [ ] Refactor Reference Data exceptions.
* [ ] Review authentication and permission errors.
* [ ] Review service rollback behaviour.
* [ ] Review provider exception translation.
* [ ] Add exception inheritance tests.
* [ ] Add exception naming architecture tests.
* [ ] Add public export tests where required.
* [ ] Run the complete test suite.
* [ ] Update the developer guide.
* [ ] Update `docs/ROADMAP.md`.

---

# Related documents

* [Platform Principles](01-platform-principles.md)
* [Project Structure and Module Boundaries](02-project-structure.md)
* [Module Conventions](03-module-conventions.md)
* [Service-Layer Conventions](04-service-layer-conventions.md)
* [Core Concepts and Shared Vocabulary](05-core-concepts.md)
* [Catalogue Framework](06-catalogue-framework.md)
* [Platform Overview and Operational Architecture](07-platform-overview.md)
* [Delivery Roadmap](../ROADMAP.md)

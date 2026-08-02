# Built-in Exception Review

## Purpose

This document reviews direct uses of Python built-in exceptions in Response Connect following the introduction of the shared platform exception hierarchy.

The review covers direct raises of:

* `RuntimeError`
* `ValueError`
* `KeyError`
* `LookupError`
* generic `Exception`

Each usage is classified as one of:

1. **Keep** — appropriate programming or value contract.
2. **Replace with platform exception** — represents an application-wide category.
3. **Replace with module exception** — requires domain-specific meaning.
4. **Remove exception flow** — normal control flow should use a return value.

This review does not require every built-in exception to be removed.

Built-in exceptions remain appropriate for internal programming contracts and value-object construction where callers are not expected to handle a Response Connect business condition.

---

# Review summary

The repository currently contains direct built-in exception usage in the following areas:

* Reference Data registry initialisation;
* Reference Data immutable definitions;
* file object-key generation;
* file-management input handling;
* catalogue validation;
* authentication and password reset;
* email services and templates;
* job-task registration and execution;
* organisation location services;
* file-processing-policy internal validation.

The principal required changes are:

1. Replace Reference Data registry `RuntimeError` with `ConfigurationError`.
2. Replace missing password-reset `SECRET_KEY` `RuntimeError` with `ConfigurationError`.
3. Refactor `PasswordResetTokenError` onto the shared hierarchy.
4. Review email configuration `RuntimeError` uses and replace them with module-specific configuration errors.
5. Keep appropriate `ValueError` uses in immutable definitions and low-level value helpers.
6. Preserve caught `KeyError`, `TypeError`, and `ValueError` where they translate malformed external or token data into domain exceptions.
7. Review Jobs registry errors as configuration errors rather than ordinary value errors.
8. Review business services that still raise `ValueError` for user-correctable business rules.

---

# Reference Data

## Registry not initialised

File:

```text
app/reference_data/__init__.py
```

Current behaviour:

```python
except KeyError as exc:
    raise RuntimeError(
        "The reference-data registry has not been "
        "initialised for this application."
    ) from exc
```

Decision:

```text
Replace with platform exception
```

Target:

```python
ConfigurationError
```

Reason:

The failure indicates that application setup is incomplete or invalid. It is not a general runtime failure.

Recommended implementation:

```python
from app.exceptions import ConfigurationError
```

```python
except KeyError as exc:
    raise ConfigurationError(
        "The reference-data registry has not been "
        "initialised for this application."
    ) from exc
```

The underlying `KeyError` should remain caught and chained.

## Reference record definitions

File:

```text
app/reference_data/definitions.py
```

Current direct raises include:

```python
raise ValueError(
    "Reference-data definitions require a stable code."
)
```

```python
raise ValueError(
    "The stable code must be supplied through the code field, "
    "not repeated inside values."
)
```

```python
raise ValueError(
    "System-owned fields must also exist in values: ..."
)
```

Decision:

```text
Keep
```

Reason:

`ReferenceRecordDefinition` and `ReferenceDatasetDefinition` are immutable value-definition objects. Their `__post_init__` methods enforce constructor contracts.

Invalid construction is a programmer or definition-authoring error, not a recoverable runtime business workflow.

Using `ValueError` here is idiomatic and keeps these low-level definitions independent of Flask and service handling.

The duplicate-code validation should also remain a `ValueError` because invalid dataset construction should fail immediately before registration.

---

# Files

## Object-key extension normalisation

File:

```text
app/files/keys.py
```

Current behaviour:

```python
if not normalised:
    raise ValueError(
        "A file extension is required."
    )
```

```python
if not normalised.replace("-", "").isalnum():
    raise ValueError(
        "The file extension contains invalid characters."
    )
```

Decision:

```text
Keep
```

Reason:

`ObjectKeyGenerator._normalise_extension()` is a private low-level value helper.

Its callers are responsible for supplying a valid extension. Invalid input represents a function contract violation rather than a user-facing Files workflow.

The public upload and processing services should validate user input earlier and translate it into `InvalidFileError` or `InvalidFileProcessingPolicyError` where needed.

No platform exception is required inside this helper.

## File manager input errors

File:

```text
app/files/manager.py
```

Decision:

```text
Review individually
```

Rules:

* user-upload validation should raise `InvalidFileError`;
* excessive size should raise `FileTooLargeError`;
* missing managed records should raise `ManagedFileNotFoundError`;
* invalid internal helper arguments may remain `ValueError`;
* database failures must raise `FilePersistenceError`;
* storage-provider failures must be translated through Files exceptions.

Any `ValueError` that can be triggered by normal user-supplied upload data should be replaced with the appropriate Files validation exception.

## File-processing-policy validation

File:

```text
app/files/processing_policies.py
```

Decision:

```text
Replace user-facing ValueError paths
```

The service already exposes:

```text
InvalidFileProcessingPolicyError
```

Internal parsing helpers may temporarily raise `ValueError`, but the public service boundary must translate them into `InvalidFileProcessingPolicyError`.

No raw `ValueError` should escape:

```python
FileProcessingPolicyService.create(...)
FileProcessingPolicyService.update(...)
FileProcessingPolicyService.replace_rules(...)
```

---

# Catalogues

## Catalogue validators

File:

```text
app/catalogues/validators.py
```

Decision:

```text
Keep only internal value-contract errors
```

The catalogue package already defines:

```text
InvalidCatalogueCodeError
```

Therefore:

* invalid catalogue stable codes should raise `InvalidCatalogueCodeError`;
* generic helpers such as colour or sort-order validators may retain `ValueError` only if they are explicitly documented as low-level reusable validators;
* public catalogue services should translate all validation failures into catalogue exceptions.

A caller using `CatalogueServiceBase` should not need to catch raw `ValueError` for ordinary catalogue input.

---

# Authentication and password reset

## PasswordResetTokenError inheritance

File:

```text
app/blueprints/auth/password_reset.py
```

Current definition:

```python
class PasswordResetTokenError(ValueError):
    """Raised when a password-reset token is invalid or expired."""
```

Decision:

```text
Replace with module exception using shared hierarchy
```

Recommended hierarchy:

```python
from app.exceptions import ValidationError
```

```python
class PasswordResetTokenError(ValidationError):
    """Raised when a password-reset token is invalid or expired."""
```

A password-reset token error is expected input validation, but it should participate in the Response Connect hierarchy rather than inherit directly from `ValueError`.

The class name and current callers can remain unchanged.

## Token payload parsing

Current code catches:

```python
except (
    KeyError,
    TypeError,
    ValueError,
) as exc:
    raise PasswordResetTokenError(...) from exc
```

Decision:

```text
Keep
```

Reason:

The token payload is external, signed input. Built-in parsing errors are correctly caught and translated into the domain-specific `PasswordResetTokenError`.

The `KeyError`, `TypeError`, and `ValueError` do not escape the authentication boundary.

## Missing SECRET_KEY

Current code:

```python
if not secret_key:
    raise RuntimeError(
        "SECRET_KEY must be configured before "
        "password-reset tokens can be generated."
    )
```

Decision:

```text
Replace with ConfigurationError
```

Recommended implementation:

```python
from app.exceptions import ConfigurationError
```

```python
if not secret_key:
    raise ConfigurationError(
        "SECRET_KEY must be configured before "
        "password-reset tokens can be generated."
    )
```

This is an installation configuration failure, not a general runtime problem.

## Password-reset maximum age

Current implementation converts configuration using:

```python
int(...)
```

This may raise `ValueError` or `TypeError` if the configured value is invalid.

Decision:

```text
Translate to ConfigurationError
```

Recommended implementation:

```python
def _get_max_age() -> int:
    configured_value = current_app.config.get(
        "PASSWORD_RESET_TOKEN_MAX_AGE",
        3600,
    )

    try:
        max_age = int(configured_value)
    except (TypeError, ValueError) as exc:
        raise ConfigurationError(
            "PASSWORD_RESET_TOKEN_MAX_AGE must "
            "be a valid integer."
        ) from exc

    if max_age <= 0:
        raise ConfigurationError(
            "PASSWORD_RESET_TOKEN_MAX_AGE must "
            "be greater than zero."
        )

    return max_age
```

---

# Email services

Files identified:

```text
app/blueprints/email/services.py
app/blueprints/email/templates.py
app/blueprints/email/handlers.py
```

Current searches indicate both `RuntimeError` and `ValueError` use.

Decision:

```text
Create an Email exception hierarchy
```

Recommended module exceptions:

```python
class EmailError(ResponseConnectError):
    """Base exception for email operations."""


class EmailConfigurationError(
    EmailError,
    ConfigurationError,
):
    """Raised when outgoing-email configuration is invalid."""


class EmailTemplateError(
    EmailError,
    ValidationError,
):
    """Raised when an email template cannot be rendered safely."""


class EmailDeliveryError(
    EmailError,
    InfrastructureError,
):
    """Raised when an email cannot be delivered."""
```

Mapping:

* missing SMTP or sender configuration → `EmailConfigurationError`;
* missing required template variables → `EmailTemplateError`;
* invalid template identity → `EmailTemplateError`;
* SMTP/provider failure → `EmailDeliveryError`;
* programmer-only registration collisions may use `ConfigurationError`.

Raw `RuntimeError` should not escape email services.

Raw SMTP or Flask-Mail exceptions should be chained as causes.

This is a separate implementation task and should be added to the roadmap rather than bundled into the current platform-only refactor.

---

# Background jobs

Files identified:

```text
app/blueprints/jobs/registry.py
app/blueprints/jobs/services.py
app/blueprints/jobs/tasks.py
```

Decision:

```text
Create a Jobs exception hierarchy
```

Suggested exceptions:

```python
class JobError(ResponseConnectError):
    """Base exception for background-job operations."""


class JobConfigurationError(
    JobError,
    ConfigurationError,
):
    """Raised when job registration is invalid."""


class JobValidationError(
    JobError,
    ValidationError,
):
    """Raised when a job request is invalid."""


class JobNotFoundError(
    JobError,
    NotFoundError,
):
    """Raised when a registered job cannot be found."""


class JobDispatchError(
    JobError,
    InfrastructureError,
):
    """Raised when a job cannot be submitted."""
```

Recommended classification:

* duplicate job registration → `JobConfigurationError`;
* unknown job type → `JobNotFoundError`;
* malformed payload → `JobValidationError`;
* queue or Celery failure → `JobDispatchError`;
* task-internal programming contracts may retain `ValueError`.

This should be recorded as a dedicated follow-up task because Jobs currently sits outside the three platform packages already migrated.

---

# Organisation location services

File:

```text
app/blueprints/org/location_services.py
```

Decision:

```text
Replace business-rule ValueError uses
```

Location service operations are application workflows.

Errors such as:

* invalid parent;
* hierarchy cycle;
* duplicate name or code;
* attempting to deactivate an in-use location;
* invalid location type;

should use explicit module exceptions rather than `ValueError`.

Suggested future hierarchy:

```python
class LocationError(ResponseConnectError):
    ...


class LocationValidationError(
    LocationError,
    ValidationError,
):
    ...


class LocationNotFoundError(
    LocationError,
    NotFoundError,
):
    ...


class LocationConflictError(
    LocationError,
    ConflictError,
):
    ...


class LocationHierarchyError(
    LocationError,
    LifecycleError,
):
    ...
```

This is business-module refactoring and should be placed in the roadmap after current platform consolidation.

---

# Direct KeyError usage

No explicit application-level `raise KeyError(...)` requiring replacement was identified.

The important `KeyError` cases are caught translation boundaries:

* Flask extension lookup;
* token payload lookup;
* registry dictionary lookup.

Rules:

* dictionary lookup internals may naturally raise `KeyError`;
* public registries should translate unknown keys to a domain `NotFoundError`;
* missing Flask extension configuration should become `ConfigurationError`;
* malformed external payloads should become validation errors.

---

# LookupError usage

No active application `raise LookupError(...)` was identified.

No change is required.

---

# Generic Exception usage

No deliberate direct:

```python
raise Exception(...)
```

was identified in the reviewed application source.

Global boundaries may still catch `Exception` where they log and safely terminate:

* Flask global error handler;
* Celery task boundary;
* CLI command boundary.

Business services should not raise generic `Exception`.

---

# Required immediate changes

The following changes belong to the current exception-hardening work:

1. Replace Reference Data registry `RuntimeError` with `ConfigurationError`.
2. Refactor `PasswordResetTokenError` to inherit from `ValidationError`.
3. Replace password-reset missing-secret `RuntimeError` with `ConfigurationError`.
4. Validate password-reset maximum-age configuration and raise `ConfigurationError`.
5. Add or update focused tests.
6. Add Reference Data and authentication exception coverage to architecture tests where appropriate.

---

# Roadmap additions

Add the following tasks to `docs/ROADMAP.md`:

```markdown
## Built-in exception review

- [x] ✅ Review direct built-in exception usage.
- [ ] 🚧 Replace Reference Data registry RuntimeError.
- [ ] ⬜ Refactor password-reset exceptions.
- [ ] ⬜ Review Email exceptions.
- [ ] ⬜ Review Jobs exceptions.
- [ ] ⬜ Review Location service exceptions.
- [ ] ⬜ Verify public services do not leak raw ValueError.
```

Under later business-module consolidation:

```markdown
- [ ] ⬜ Add Email module exception hierarchy.
- [ ] ⬜ Add Jobs module exception hierarchy.
- [ ] ⬜ Add Location module exception hierarchy.
```

---

# Review conclusion

Built-in exceptions are not inherently prohibited.

They remain appropriate for:

* immutable value-object construction;
* private parsing helpers;
* programmer contracts;
* standard-library conversion failures that are immediately translated.

They should be replaced when they represent:

* application configuration;
* a user-correctable business condition;
* a missing domain record;
* a lifecycle conflict;
* infrastructure or persistence failure;
* a public service contract.

The highest-priority corrections are the Reference Data registry and password-reset configuration paths.

The Email, Jobs and Location modules require their own domain exception hierarchies, but those changes should be handled as explicit roadmap tasks rather than folded into the completed platform-package migration.

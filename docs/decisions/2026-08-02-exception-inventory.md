# Existing Exception Inventory

## Purpose

This document inventories the custom exceptions currently defined in Response Connect before they are migrated onto the shared hierarchy described in `docs/architecture/08-exception-hierarchy.md`.

The inventory records:

* the current inheritance;
* the error’s purpose;
* whether it forms part of a public package API;
* the proposed platform category;
* whether the current name should be retained;
* known usage and test coverage;
* implementation observations.

No exception classes should be changed until this inventory has been reviewed.

# Summary

The current platform defines custom exceptions in three principal packages:

```text
app/catalogues/exceptions.py
app/files/exceptions.py
app/reference_data/exceptions.py
```

At present, each package defines an independent base exception inheriting directly from Python’s `Exception`.

The current trees are:

```text
Exception
├── CatalogueError
├── StorageError
├── FileManagementError
├── FileProcessingPolicyError
└── ReferenceDataError
```

The target architecture introduces:

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

Module-specific exceptions should retain their domain-specific names while also inheriting from the appropriate shared category.

# Catalogue exceptions

Source:

```text
app/catalogues/exceptions.py
```

## CatalogueError

| Property     | Review                               |
| ------------ | ------------------------------------ |
| Current base | `Exception`                          |
| Purpose      | Base class for catalogue operations  |
| Public       | Yes                                  |
| Target base  | `ResponseConnectError`               |
| Retain name  | Yes                                  |
| Notes        | Suitable module-level base exception |

Proposed definition:

```python
class CatalogueError(ResponseConnectError):
    """Base exception for catalogue operations."""
```

## CatalogueRecordNotFoundError

| Property          | Review                                    |
| ----------------- | ----------------------------------------- |
| Current base      | `CatalogueError`                          |
| Purpose           | Requested catalogue record does not exist |
| Public            | Yes                                       |
| Target category   | `NotFoundError`                           |
| Retain name       | Yes                                       |
| Expected handling | 404 or service-level not-found handling   |
| Logging           | Normally no                               |

Proposed inheritance:

```python
class CatalogueRecordNotFoundError(
    CatalogueError,
    NotFoundError,
):
    ...
```

## InvalidCatalogueCodeError

| Property          | Review                           |
| ----------------- | -------------------------------- |
| Current base      | `CatalogueError`                 |
| Purpose           | Stable catalogue code is invalid |
| Public            | Yes                              |
| Target category   | `ValidationError`                |
| Retain name       | Yes                              |
| Expected handling | Form or command validation       |
| Logging           | No                               |

Proposed inheritance:

```python
class InvalidCatalogueCodeError(
    CatalogueError,
    ValidationError,
):
    ...
```

## CatalogueCodeConflictError

| Property          | Review                     |
| ----------------- | -------------------------- |
| Current base      | `CatalogueError`           |
| Purpose           | Stable code already exists |
| Public            | Yes                        |
| Target category   | `ConflictError`            |
| Retain name       | Yes                        |
| Expected handling | Field error or HTTP 409    |
| Logging           | No                         |

## CatalogueNameConflictError

| Property          | Review                                     |
| ----------------- | ------------------------------------------ |
| Current base      | `CatalogueError`                           |
| Purpose           | Display name conflicts with another record |
| Public            | Yes                                        |
| Target category   | `ConflictError`                            |
| Retain name       | Yes                                        |
| Expected handling | Field error or HTTP 409                    |
| Logging           | No                                         |

## ProtectedSystemRecordError

| Property             | Review                                                                                           |
| -------------------- | ------------------------------------------------------------------------------------------------ |
| Current base         | `CatalogueError`                                                                                 |
| Purpose              | Illegal modification or deletion of a protected system record                                    |
| Public               | Yes                                                                                              |
| Target category      | `LifecycleError`                                                                                 |
| Alternative category | `ConflictError`                                                                                  |
| Retain name          | Yes                                                                                              |
| Recommendation       | Use `LifecycleError` because the attempted operation is invalid for the record’s ownership state |
| Logging              | No                                                                                               |

Proposed inheritance:

```python
class ProtectedSystemRecordError(
    CatalogueError,
    LifecycleError,
):
    ...
```

## CatalogueRecordInUseError

| Property        | Review                                                   |
| --------------- | -------------------------------------------------------- |
| Current base    | `CatalogueError`                                         |
| Purpose         | Record cannot be deleted or deactivated while referenced |
| Public          | Yes                                                      |
| Target category | `ConflictError`                                          |
| Retain name     | Yes                                                      |
| Logging         | No                                                       |

## CataloguePersistenceError

| Property        | Review                                 |
| --------------- | -------------------------------------- |
| Current base    | `CatalogueError`                       |
| Purpose         | Catalogue state cannot be persisted    |
| Public          | Yes                                    |
| Target category | `PersistenceError`                     |
| Retain name     | Yes                                    |
| Logging         | Yes, at the service or global boundary |

# Catalogue public API review

All eight catalogue exceptions are exported from `app.catalogues` through `__all__`.

Recommendation:

* retain all existing public names;
* change inheritance only;
* preserve current import paths;
* add inheritance tests;
* do not require callers to update imports.

# Object-storage exceptions

Source:

```text
app/files/exceptions.py
```

## StorageError

| Property              | Review                                                      |
| --------------------- | ----------------------------------------------------------- |
| Current base          | `Exception`                                                 |
| Purpose               | Base class for object-storage failures                      |
| Public package export | No                                                          |
| Used internally       | Yes                                                         |
| Target base           | `InfrastructureError`                                       |
| Retain name           | Yes                                                         |
| Notes                 | The module base can itself represent infrastructure failure |

Proposed definition:

```python
class StorageError(InfrastructureError):
    """Base exception for object-storage failures."""
```

Unlike most module bases, `StorageError` has a clear platform category and does not need to inherit directly from `ResponseConnectError`.

## StorageConfigurationError

| Property              | Review                                               |
| --------------------- | ---------------------------------------------------- |
| Current base          | `StorageError`                                       |
| Purpose               | Required storage configuration is missing or invalid |
| Public package export | No                                                   |
| Target category       | `ConfigurationError`                                 |
| Retain name           | Yes                                                  |
| Logging               | Yes                                                  |

Proposed inheritance:

```python
class StorageConfigurationError(
    StorageError,
    ConfigurationError,
):
    ...
```

This creates multiple inheritance between two platform categories because `StorageError` already derives from `InfrastructureError`.

A cleaner alternative is therefore recommended:

```python
class StorageError(ResponseConnectError):
    ...

class StorageConfigurationError(
    StorageError,
    ConfigurationError,
):
    ...
```

This preserves the module-category pattern consistently.

## StorageConnectionError

| Property              | Review                                   |
| --------------------- | ---------------------------------------- |
| Current base          | `StorageError`                           |
| Purpose               | Object-storage service cannot be reached |
| Public package export | No                                       |
| Target category       | `InfrastructureError`                    |
| Retain name           | Yes                                      |
| Retryable             | Potentially                              |
| Logging               | Yes                                      |

## StorageObjectNotFoundError

| Property              | Review                                  |
| --------------------- | --------------------------------------- |
| Current base          | `StorageError`                          |
| Purpose               | Requested object is absent from storage |
| Public package export | No                                      |
| Target category       | `NotFoundError`                         |
| Retain name           | Yes                                     |
| Logging               | Depends on context                      |

A missing object may indicate:

* an ordinary request for an unavailable object;
* object-store/database inconsistency;
* external deletion;
* failed upload compensation.

The provider should raise `StorageObjectNotFoundError`. The higher Files service decides whether this becomes:

* `ManagedFileNotFoundError`;
* a persistence/integrity failure;
* a reconciliation warning.

# Managed-file exceptions

## FileManagementError

| Property              | Review                                 |
| --------------------- | -------------------------------------- |
| Current base          | `Exception`                            |
| Purpose               | Base class for managed-file operations |
| Public package export | No                                     |
| Target base           | `ResponseConnectError`                 |
| Retain name           | Yes                                    |

## InvalidFileError

| Property              | Review                   |
| --------------------- | ------------------------ |
| Current base          | `FileManagementError`    |
| Purpose               | Uploaded file is invalid |
| Public package export | No                       |
| Target category       | `ValidationError`        |
| Retain name           | Yes                      |
| Logging               | No                       |

## FileTooLargeError

| Property              | Review                                 |
| --------------------- | -------------------------------------- |
| Current base          | `InvalidFileError`                     |
| Purpose               | File exceeds the configured size limit |
| Public package export | No                                     |
| Target category       | Inherited `ValidationError`            |
| Retain name           | Yes                                    |
| Logging               | No                                     |

No additional platform base is required because `InvalidFileError` will already derive from `ValidationError`.

## FilePersistenceError

| Property              | Review                                           |
| --------------------- | ------------------------------------------------ |
| Current base          | `FileManagementError`                            |
| Purpose               | Managed-file metadata cannot be persisted safely |
| Public package export | No                                               |
| Target category       | `PersistenceError`                               |
| Retain name           | Yes                                              |
| Logging               | Yes                                              |

## ManagedFileNotFoundError

| Property              | Review                                       |
| --------------------- | -------------------------------------------- |
| Current base          | `FileManagementError`                        |
| Purpose               | Managed-file database record cannot be found |
| Public package export | No                                           |
| Target category       | `NotFoundError`                              |
| Retain name           | Yes                                          |
| Logging               | Normally no                                  |

## DeletedFileError

| Property              | Review                                     |
| --------------------- | ------------------------------------------ |
| Current base          | `FileManagementError`                      |
| Purpose               | Operation attempted on a soft-deleted file |
| Public package export | No                                         |
| Target category       | `LifecycleError`                           |
| Retain name           | Yes                                        |
| Logging               | No                                         |

The file exists, but its lifecycle state prevents the requested operation. `LifecycleError` is therefore preferable to `NotFoundError`.

# File-processing-policy exceptions

## FileProcessingPolicyError

| Property              | Review                                      |
| --------------------- | ------------------------------------------- |
| Current base          | `Exception`                                 |
| Purpose               | Base class for processing-policy operations |
| Public package export | No                                          |
| Target base           | `ResponseConnectError`                      |
| Retain name           | Yes                                         |

## FileProcessingPolicyNotFoundError

| Property        | Review                            |
| --------------- | --------------------------------- |
| Current base    | `FileProcessingPolicyError`       |
| Purpose         | Processing policy cannot be found |
| Target category | `NotFoundError`                   |
| Retain name     | Yes                               |
| Tests           | Covered by service tests          |

## FileProcessingPolicyCodeConflictError

| Property        | Review                                |
| --------------- | ------------------------------------- |
| Current base    | `FileProcessingPolicyError`           |
| Purpose         | Processing-policy code already exists |
| Target category | `ConflictError`                       |
| Retain name     | Yes                                   |
| Tests           | Covered                               |

## FileProcessingPolicyNameConflictError

| Property        | Review                                |
| --------------- | ------------------------------------- |
| Current base    | `FileProcessingPolicyError`           |
| Purpose         | Processing-policy name already exists |
| Target category | `ConflictError`                       |
| Retain name     | Yes                                   |
| Tests           | Covered                               |

## InvalidFileProcessingPolicyError

| Property        | Review                                    |
| --------------- | ----------------------------------------- |
| Current base    | `FileProcessingPolicyError`               |
| Purpose         | Policy configuration or rules are invalid |
| Target category | `ValidationError`                         |
| Retain name     | Yes                                       |
| Tests           | Covered                                   |

## ProtectedFileProcessingPolicyError

| Property             | Review                                                                |
| -------------------- | --------------------------------------------------------------------- |
| Current base         | `FileProcessingPolicyError`                                           |
| Purpose              | Protected system policy is modified illegally                         |
| Target category      | `LifecycleError`                                                      |
| Alternative category | `ConflictError`                                                       |
| Retain name          | Yes                                                                   |
| Recommendation       | Use `LifecycleError` for consistency with protected catalogue records |
| Tests                | Covered                                                               |

## FileProcessingPolicyInUseError

| Property        | Review                                                                   |
| --------------- | ------------------------------------------------------------------------ |
| Current base    | `FileProcessingPolicyError`                                              |
| Purpose         | Policy cannot be deleted while referenced                                |
| Target category | `ConflictError`                                                          |
| Retain name     | Yes                                                                      |
| Current usage   | Defined but not yet actively used because File Types are not implemented |
| Tests           | Not currently covered                                                    |
| Recommendation  | Retain for upcoming File Type work                                       |

## FileProcessingPolicyPersistenceError

| Property        | Review                                                                 |
| --------------- | ---------------------------------------------------------------------- |
| Current base    | `FileProcessingPolicyError`                                            |
| Purpose         | Policy state cannot be persisted                                       |
| Target category | `PersistenceError`                                                     |
| Retain name     | Yes                                                                    |
| Tests           | Indirectly exercised; explicit failure-translation test still required |

# Files public API review

`app.files.__all__` currently exports managers, models, providers, commands and service factories, but does not export any Files exceptions.

Decision required during refactor:

1. Keep exceptions available only from `app.files.exceptions`; or
2. Export caller-facing exceptions through `app.files`.

Recommendation:

Export only exceptions that external modules are expected to catch:

```text
FileManagementError
InvalidFileError
FileTooLargeError
FilePersistenceError
ManagedFileNotFoundError
DeletedFileError

FileProcessingPolicyError
FileProcessingPolicyNotFoundError
FileProcessingPolicyCodeConflictError
FileProcessingPolicyNameConflictError
InvalidFileProcessingPolicyError
ProtectedFileProcessingPolicyError
FileProcessingPolicyInUseError
FileProcessingPolicyPersistenceError
```

Keep storage-provider exceptions private unless a public service contract explicitly requires callers to handle them.

# Reference Data exceptions

Source:

```text
app/reference_data/exceptions.py
```

## ReferenceDataError

| Property              | Review                                   |
| --------------------- | ---------------------------------------- |
| Current base          | `Exception`                              |
| Purpose               | Base class for Reference Data operations |
| Public package export | No                                       |
| Target base           | `ResponseConnectError`                   |
| Retain name           | Yes                                      |

## DuplicateReferenceDatasetError

| Property        | Review                                                                    |
| --------------- | ------------------------------------------------------------------------- |
| Current base    | `ReferenceDataError`                                                      |
| Purpose         | Dataset registered more than once                                         |
| Target category | `ConfigurationError`                                                      |
| Retain name     | Yes                                                                       |
| Logging         | Yes during application setup                                              |
| Notes           | This represents invalid application composition rather than user conflict |

## ReferenceDatasetNotFoundError

| Property             | Review                                                                                                                                          |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Current base         | `ReferenceDataError`                                                                                                                            |
| Purpose              | Requested dataset is not registered                                                                                                             |
| Target category      | `NotFoundError`                                                                                                                                 |
| Alternative category | `ConfigurationError`                                                                                                                            |
| Retain name          | Yes                                                                                                                                             |
| Recommendation       | Use `NotFoundError` when requested by CLI or caller; missing expected installation registration may separately surface as configuration failure |

## ReferenceDataConflictError

| Property        | Review                                                   |
| --------------- | -------------------------------------------------------- |
| Current base    | `ReferenceDataError`                                     |
| Purpose         | System definition conflicts with incompatible local data |
| Target category | `ConflictError`                                          |
| Retain name     | Yes                                                      |
| Logging         | Warning                                                  |
| Tests           | Conflict tests should be added                           |

## ReferenceDataSynchronisationError

| Property             | Review                                                                |
| -------------------- | --------------------------------------------------------------------- |
| Current base         | `ReferenceDataError`                                                  |
| Purpose              | Reference data cannot be synchronised safely                          |
| Target category      | `PersistenceError`                                                    |
| Possible alternative | `InfrastructureError` for provider-dependent datasets                 |
| Retain name          | Yes                                                                   |
| Recommendation       | Use `PersistenceError` for the current database-backed implementation |
| Logging              | Yes                                                                   |

# Reference Data public API review

Reference Data exceptions are not currently exported through `app.reference_data.__all__`.

Recommendation:

Export the caller-facing hierarchy through `app.reference_data`:

```text
ReferenceDataError
DuplicateReferenceDatasetError
ReferenceDatasetNotFoundError
ReferenceDataConflictError
ReferenceDataSynchronisationError
```

The CLI and future upgrade runner are expected to catch these exceptions, so they should form part of the deliberate public interface.

# Authentication and permissions review

No dedicated authentication or permission exception hierarchy was identified in the current platform exception files.

Current authorisation behaviour appears to be implemented primarily through:

* decorators;
* Flask redirects;
* HTTP abort responses;
* validation and token handling.

This means the following architecture work remains:

* review authentication modules for raw `RuntimeError`, `ValueError` and provider exceptions;
* decide whether service-layer authentication operations need `AuthenticationError`;
* decide whether `PermissionDeniedError` should be raised by reusable authorisation services;
* preserve normal Flask decorator behaviour where an exception would not add value;
* add security-event integration later through the Event Journal.

The shared hierarchy should still include `PermissionDeniedError` now, even if no current caller raises it.

# Other exception-like behaviour found

The review should also inspect code that raises built-in exceptions directly.

Likely examples include:

```text
RuntimeError
ValueError
KeyError
LookupError
```

Some built-ins are appropriate for programmer-facing contracts, but others may currently represent platform failures.

Known example:

```python
get_reference_data_registry()
```

raises `RuntimeError` when the registry has not been initialised.

Target recommendation:

```python
raise ConfigurationError(
    "The reference-data registry has not been initialised."
)
```

This should be performed during the Reference Data exception refactor.

# Target mapping summary

| Current exception                       | Target platform category           |
| --------------------------------------- | ---------------------------------- |
| `CatalogueError`                        | `ResponseConnectError`             |
| `CatalogueRecordNotFoundError`          | `NotFoundError`                    |
| `InvalidCatalogueCodeError`             | `ValidationError`                  |
| `CatalogueCodeConflictError`            | `ConflictError`                    |
| `CatalogueNameConflictError`            | `ConflictError`                    |
| `ProtectedSystemRecordError`            | `LifecycleError`                   |
| `CatalogueRecordInUseError`             | `ConflictError`                    |
| `CataloguePersistenceError`             | `PersistenceError`                 |
| `StorageError`                          | `ResponseConnectError` module base |
| `StorageConfigurationError`             | `ConfigurationError`               |
| `StorageConnectionError`                | `InfrastructureError`              |
| `StorageObjectNotFoundError`            | `NotFoundError`                    |
| `FileManagementError`                   | `ResponseConnectError`             |
| `InvalidFileError`                      | `ValidationError`                  |
| `FileTooLargeError`                     | inherited validation category      |
| `FilePersistenceError`                  | `PersistenceError`                 |
| `ManagedFileNotFoundError`              | `NotFoundError`                    |
| `DeletedFileError`                      | `LifecycleError`                   |
| `FileProcessingPolicyError`             | `ResponseConnectError`             |
| `FileProcessingPolicyNotFoundError`     | `NotFoundError`                    |
| `FileProcessingPolicyCodeConflictError` | `ConflictError`                    |
| `FileProcessingPolicyNameConflictError` | `ConflictError`                    |
| `InvalidFileProcessingPolicyError`      | `ValidationError`                  |
| `ProtectedFileProcessingPolicyError`    | `LifecycleError`                   |
| `FileProcessingPolicyInUseError`        | `ConflictError`                    |
| `FileProcessingPolicyPersistenceError`  | `PersistenceError`                 |
| `ReferenceDataError`                    | `ResponseConnectError`             |
| `DuplicateReferenceDatasetError`        | `ConfigurationError`               |
| `ReferenceDatasetNotFoundError`         | `NotFoundError`                    |
| `ReferenceDataConflictError`            | `ConflictError`                    |
| `ReferenceDataSynchronisationError`     | `PersistenceError`                 |

# Public-name compatibility decision

The refactor should preserve all current exception class names.

Only inheritance and public exports should change.

Benefits:

* existing tests remain meaningful;
* callers do not require renaming;
* Git history remains easy to follow;
* error messages can remain unchanged;
* the refactor remains architectural rather than behavioural.

# Refactor order

The implementation should proceed in this order:

1. Create `app/exceptions.py`.
2. Add shared platform exception classes.
3. Add unit tests for the shared hierarchy.
4. Refactor `app/catalogues/exceptions.py`.
5. Run catalogue and architecture tests.
6. Refactor storage and managed-file exceptions.
7. Refactor file-processing-policy exceptions.
8. Run the complete Files test suite.
9. Refactor Reference Data exceptions.
10. Replace the Reference Data registry `RuntimeError`.
11. Review public exports.
12. Add architecture tests for exception inheritance and naming.
13. Run the complete test suite.
14. Update the roadmap.
15. Remove this temporary inventory after its conclusions are incorporated into permanent documentation and tests.

# Additional observations

## Duplicate Files service import

`app/files/__init__.py` currently imports `FileProcessingPolicyService` twice in adjacent import blocks.

This is not part of the exception refactor, but should be added to the roadmap’s consolidation cleanup and corrected during the public API review.

## Files exception exports

The Files package currently exposes no exception classes at package level.

The refactor should make an explicit decision rather than leaving this accidental.

## Reference Data exception exports

The Reference Data package also currently exposes no exception classes at package level.

Because CLI commands and future upgrade workflows need to handle these failures, public exports are recommended.

## Storage exceptions

Storage exceptions should remain hidden behind Files services wherever possible.

Business modules must not depend on the S3 provider’s exception vocabulary.

# Review decision

The existing exception names are generally clear and domain-specific.

The main architectural deficiency is not naming but independent inheritance from `Exception`.

The refactor should therefore:

* introduce the shared platform hierarchy;
* preserve existing names;
* add module-category multiple inheritance;
* translate the remaining built-in configuration failures;
* make public exports deliberate;
* add architecture fitness tests;
* avoid changing user-facing behaviour unnecessarily.

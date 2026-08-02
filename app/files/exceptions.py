from app.exceptions import (
    ConfigurationError,
    InfrastructureError,
    LifecycleError,
    NotFoundError,
    PersistenceError,
    ResponseConnectError,
    ValidationError,
    ConflictError,
)

class StorageError(ResponseConnectError):
    """Base exception for object-storage failures."""


class StorageConfigurationError(
    StorageError,
    ConfigurationError,
):
    """Raised when required storage configuration is missing."""


class StorageConnectionError(
    StorageError,
    InfrastructureError,
):
    """Raised when the object-storage service cannot be reached."""


class StorageObjectNotFoundError(
    StorageError,
    NotFoundError,
):
    """Raised when a requested object does not exist."""

class FileManagementError(ResponseConnectError):
    """Base exception for managed-file operations."""


class InvalidFileError(
    FileManagementError,
    ValidationError,
):
    """Raised when an uploaded file is invalid."""


class FileTooLargeError(InvalidFileError):
    """Raised when a file exceeds the configured limit."""


class FilePersistenceError(
    FileManagementError,
    PersistenceError,
):
    """Raised when file metadata cannot be persisted safely."""


class ManagedFileNotFoundError(
    FileManagementError,
    NotFoundError,
):
    """Raised when a managed file record cannot be found."""


class DeletedFileError(
    FileManagementError,
    LifecycleError,
):
    """Raised when an operation is attempted on a deleted file."""

class FileProcessingPolicyError(ResponseConnectError):
    """Base exception for file-processing policy operations."""


class FileProcessingPolicyNotFoundError(
    FileProcessingPolicyError,
    NotFoundError,
):
    """Raised when a processing policy cannot be found."""


class FileProcessingPolicyCodeConflictError(
    FileProcessingPolicyError,
    ConflictError,
):
    """Raised when a processing-policy code is already used."""


class FileProcessingPolicyNameConflictError(
    FileProcessingPolicyError,
    ConflictError,
):
    """Raised when a processing-policy name is already used."""


class InvalidFileProcessingPolicyError(
    FileProcessingPolicyError,
    ValidationError,
):
    """Raised when processing-policy settings are invalid."""


class ProtectedFileProcessingPolicyError(
    FileProcessingPolicyError,
    LifecycleError,
):
    """Raised when a protected system policy is modified illegally."""


class FileProcessingPolicyInUseError(
    FileProcessingPolicyError,
    ConflictError,
):
    """Raised when a processing policy is still referenced."""


class FileProcessingPolicyPersistenceError(
    FileProcessingPolicyError,
    PersistenceError,
):
    """Raised when processing-policy state cannot be persisted."""
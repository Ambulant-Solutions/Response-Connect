class StorageError(Exception):
    """Base exception for object-storage failures."""


class StorageConfigurationError(StorageError):
    """Raised when required storage configuration is missing."""


class StorageConnectionError(StorageError):
    """Raised when the object-storage service cannot be reached."""


class StorageObjectNotFoundError(StorageError):
    """Raised when a requested object does not exist."""


class FileManagementError(Exception):
    """Base exception for managed-file operations."""


class InvalidFileError(FileManagementError):
    """Raised when an uploaded file is invalid."""


class FileTooLargeError(InvalidFileError):
    """Raised when a file exceeds the configured limit."""


class FilePersistenceError(FileManagementError):
    """Raised when file metadata cannot be persisted safely."""


class ManagedFileNotFoundError(FileManagementError):
    """Raised when a managed file record cannot be found."""


class DeletedFileError(FileManagementError):
    """Raised when an operation is attempted on a deleted file."""

class FileProcessingPolicyError(Exception):
    """Base exception for file-processing policy operations."""


class FileProcessingPolicyNotFoundError(
    FileProcessingPolicyError
):
    """Raised when a processing policy cannot be found."""


class FileProcessingPolicyCodeConflictError(
    FileProcessingPolicyError
):
    """Raised when a processing-policy code is already used."""


class FileProcessingPolicyNameConflictError(
    FileProcessingPolicyError
):
    """Raised when a processing-policy name is already used."""


class InvalidFileProcessingPolicyError(
    FileProcessingPolicyError
):
    """Raised when processing-policy settings are invalid."""


class ProtectedFileProcessingPolicyError(
    FileProcessingPolicyError
):
    """Raised when a protected system policy is modified illegally."""


class FileProcessingPolicyInUseError(
    FileProcessingPolicyError
):
    """Raised when a processing policy is still referenced."""


class FileProcessingPolicyPersistenceError(
    FileProcessingPolicyError
):
    """Raised when processing-policy state cannot be persisted."""
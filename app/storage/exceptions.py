class StorageError(Exception):
    """Base exception for object-storage failures."""


class StorageConfigurationError(StorageError):
    """Raised when required storage configuration is missing."""


class StorageConnectionError(StorageError):
    """Raised when the object-storage service cannot be reached."""


class StorageObjectNotFoundError(StorageError):
    """Raised when a requested object does not exist."""
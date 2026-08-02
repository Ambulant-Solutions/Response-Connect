from app.exceptions import (
    ConfigurationError,
    NotFoundError,
    PersistenceError,
    ResponseConnectError,
    ConflictError,
)

class ReferenceDataError(ResponseConnectError):
    """Base exception for reference-data operations."""


class DuplicateReferenceDatasetError(
    ReferenceDataError,
    ConfigurationError,
):
    """Raised when a dataset name is registered more than once."""


class ReferenceDatasetNotFoundError(
    ReferenceDataError,
    NotFoundError,
):
    """Raised when a requested dataset is not registered."""


class ReferenceDataConflictError(
    ReferenceDataError,
    ConflictError,
):
    """
    Raised when a system definition conflicts with incompatible local data.
    """


class ReferenceDataSynchronisationError(
    ReferenceDataError,
    PersistenceError,
):
    """Raised when reference data cannot be synchronised safely."""

__all__ = [
    "DuplicateReferenceDatasetError",
    "ReferenceDataConflictError",
    "ReferenceDataError",
    "ReferenceDataSynchronisationError",
    "ReferenceDatasetNotFoundError",
]
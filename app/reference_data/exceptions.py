class ReferenceDataError(Exception):
    """Base exception for reference-data operations."""


class DuplicateReferenceDatasetError(ReferenceDataError):
    """Raised when a dataset name is registered more than once."""


class ReferenceDatasetNotFoundError(ReferenceDataError):
    """Raised when a requested dataset is not registered."""


class ReferenceDataConflictError(ReferenceDataError):
    """
    Raised when a system definition conflicts with incompatible local data.
    """


class ReferenceDataSynchronisationError(ReferenceDataError):
    """Raised when reference data cannot be synchronised safely."""
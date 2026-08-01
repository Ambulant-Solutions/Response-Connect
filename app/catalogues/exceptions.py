class CatalogueError(Exception):
    """Base exception for catalogue operations."""


class CatalogueRecordNotFoundError(CatalogueError):
    """Raised when a catalogue record cannot be found."""


class InvalidCatalogueCodeError(CatalogueError):
    """Raised when a catalogue code is invalid."""


class CatalogueCodeConflictError(CatalogueError):
    """Raised when a catalogue code is already in use."""


class CatalogueNameConflictError(CatalogueError):
    """Raised when a catalogue name conflicts with another record."""


class ProtectedSystemRecordError(CatalogueError):
    """Raised when a protected system record is modified illegally."""


class CatalogueRecordInUseError(CatalogueError):
    """Raised when a catalogue record cannot be deleted because it is in use."""


class CataloguePersistenceError(CatalogueError):
    """Raised when catalogue state cannot be persisted."""
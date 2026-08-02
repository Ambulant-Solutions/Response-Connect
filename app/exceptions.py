"""Shared Response Connect exception categories.

These exceptions define the platform-wide error categories used by
services, infrastructure adapters, routes, CLI commands, workers, and
future Event Journal integrations.
"""


class ResponseConnectError(Exception):
    """Base class for expected Response Connect application errors."""


class ValidationError(ResponseConnectError):
    """Raised when supplied application data is invalid."""


class NotFoundError(ResponseConnectError):
    """Raised when a requested domain record cannot be found."""


class ConflictError(ResponseConnectError):
    """Raised when a request conflicts with existing application state."""


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


__all__ = [
    "ConfigurationError",
    "ConflictError",
    "InfrastructureError",
    "LifecycleError",
    "NotFoundError",
    "PermissionDeniedError",
    "PersistenceError",
    "ResponseConnectError",
    "ValidationError",
]
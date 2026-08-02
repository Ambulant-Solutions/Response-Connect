from app.exceptions import (
    ConfigurationError,
    ConflictError,
    InfrastructureError,
    LifecycleError,
    NotFoundError,
    PermissionDeniedError,
    PersistenceError,
    ResponseConnectError,
    ValidationError,
)


PLATFORM_EXCEPTIONS = (
    ValidationError,
    NotFoundError,
    ConflictError,
    PermissionDeniedError,
    LifecycleError,
    PersistenceError,
    InfrastructureError,
    ConfigurationError,
)


def test_response_connect_error_inherits_from_exception() -> None:
    assert issubclass(
        ResponseConnectError,
        Exception,
    )


def test_platform_errors_inherit_from_response_connect_error(
) -> None:
    for exception_class in PLATFORM_EXCEPTIONS:
        assert issubclass(
            exception_class,
            ResponseConnectError,
        )


def test_platform_error_message_is_preserved() -> None:
    error = ValidationError(
        "The supplied value is invalid."
    )

    assert str(error) == (
        "The supplied value is invalid."
    )


def test_platform_error_categories_are_distinct() -> None:
    assert ValidationError is not ConflictError
    assert NotFoundError is not PersistenceError
    assert (
        InfrastructureError
        is not ConfigurationError
    )
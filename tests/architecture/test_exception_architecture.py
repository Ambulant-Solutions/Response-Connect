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


PLATFORM_EXCEPTION_CLASSES = (
    ResponseConnectError,
    ValidationError,
    NotFoundError,
    ConflictError,
    PermissionDeniedError,
    LifecycleError,
    PersistenceError,
    InfrastructureError,
    ConfigurationError,
)


def test_platform_exception_names_end_with_error(
) -> None:
    invalid_names = [
        exception_class.__name__
        for exception_class
        in PLATFORM_EXCEPTION_CLASSES
        if not exception_class.__name__.endswith(
            "Error"
        )
    ]

    assert not invalid_names, (
        "Platform exception names must end with "
        "'Error':\n"
        + "\n".join(
            sorted(invalid_names)
        )
    )


def test_platform_exception_categories_inherit_from_base(
) -> None:
    invalid_classes = [
        exception_class.__name__
        for exception_class
        in PLATFORM_EXCEPTION_CLASSES
        if exception_class is not ResponseConnectError
        and not issubclass(
            exception_class,
            ResponseConnectError,
        )
    ]

    assert not invalid_classes, (
        "Platform exception categories must inherit "
        "from ResponseConnectError:\n"
        + "\n".join(
            sorted(invalid_classes)
        )
    )
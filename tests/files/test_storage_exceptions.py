from app.exceptions import (
    ConfigurationError,
    InfrastructureError,
    NotFoundError,
    ResponseConnectError,
)
from app.files.exceptions import (
    StorageConfigurationError,
    StorageConnectionError,
    StorageError,
    StorageObjectNotFoundError,
)


def test_storage_error_inherits_from_platform_base() -> None:
    assert issubclass(
        StorageError,
        ResponseConnectError,
    )


def test_storage_configuration_error_categories() -> None:
    assert issubclass(
        StorageConfigurationError,
        StorageError,
    )
    assert issubclass(
        StorageConfigurationError,
        ConfigurationError,
    )


def test_storage_connection_error_categories() -> None:
    assert issubclass(
        StorageConnectionError,
        StorageError,
    )
    assert issubclass(
        StorageConnectionError,
        InfrastructureError,
    )


def test_storage_object_not_found_error_categories() -> None:
    assert issubclass(
        StorageObjectNotFoundError,
        StorageError,
    )
    assert issubclass(
        StorageObjectNotFoundError,
        NotFoundError,
    )


def test_storage_error_message_is_preserved() -> None:
    error = StorageConnectionError(
        "The object-storage service is unavailable."
    )

    assert str(error) == (
        "The object-storage service is unavailable."
    )
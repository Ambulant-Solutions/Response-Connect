from app.exceptions import (
    LifecycleError,
    NotFoundError,
    PersistenceError,
    ResponseConnectError,
    ValidationError,
)
from app.files.exceptions import (
    DeletedFileError,
    FileManagementError,
    FilePersistenceError,
    FileTooLargeError,
    InvalidFileError,
    ManagedFileNotFoundError,
)


def test_file_management_error_inherits_from_platform_base() -> None:
    assert issubclass(
        FileManagementError,
        ResponseConnectError,
    )


def test_invalid_file_error_categories() -> None:
    assert issubclass(
        InvalidFileError,
        FileManagementError,
    )
    assert issubclass(
        InvalidFileError,
        ValidationError,
    )


def test_file_too_large_error_categories() -> None:
    assert issubclass(
        FileTooLargeError,
        InvalidFileError,
    )
    assert issubclass(
        FileTooLargeError,
        ValidationError,
    )


def test_file_persistence_error_categories() -> None:
    assert issubclass(
        FilePersistenceError,
        FileManagementError,
    )
    assert issubclass(
        FilePersistenceError,
        PersistenceError,
    )


def test_managed_file_not_found_error_categories() -> None:
    assert issubclass(
        ManagedFileNotFoundError,
        FileManagementError,
    )
    assert issubclass(
        ManagedFileNotFoundError,
        NotFoundError,
    )


def test_deleted_file_error_categories() -> None:
    assert issubclass(
        DeletedFileError,
        FileManagementError,
    )
    assert issubclass(
        DeletedFileError,
        LifecycleError,
    )


def test_file_management_error_message_is_preserved() -> None:
    error = DeletedFileError(
        "The managed file has been deleted."
    )

    assert str(error) == (
        "The managed file has been deleted."
    )
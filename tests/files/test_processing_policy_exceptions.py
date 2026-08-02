from app.exceptions import (
    ConflictError,
    LifecycleError,
    NotFoundError,
    PersistenceError,
    ResponseConnectError,
    ValidationError,
)
from app.files.exceptions import (
    FileProcessingPolicyCodeConflictError,
    FileProcessingPolicyError,
    FileProcessingPolicyInUseError,
    FileProcessingPolicyNameConflictError,
    FileProcessingPolicyNotFoundError,
    FileProcessingPolicyPersistenceError,
    InvalidFileProcessingPolicyError,
    ProtectedFileProcessingPolicyError,
)


def test_processing_policy_error_inherits_from_platform_base() -> None:
    assert issubclass(
        FileProcessingPolicyError,
        ResponseConnectError,
    )


def test_processing_policy_not_found_categories() -> None:
    assert issubclass(
        FileProcessingPolicyNotFoundError,
        FileProcessingPolicyError,
    )
    assert issubclass(
        FileProcessingPolicyNotFoundError,
        NotFoundError,
    )


def test_processing_policy_conflict_categories() -> None:
    conflict_errors = (
        FileProcessingPolicyCodeConflictError,
        FileProcessingPolicyNameConflictError,
        FileProcessingPolicyInUseError,
    )

    for exception_class in conflict_errors:
        assert issubclass(
            exception_class,
            FileProcessingPolicyError,
        )
        assert issubclass(
            exception_class,
            ConflictError,
        )


def test_invalid_processing_policy_categories() -> None:
    assert issubclass(
        InvalidFileProcessingPolicyError,
        FileProcessingPolicyError,
    )
    assert issubclass(
        InvalidFileProcessingPolicyError,
        ValidationError,
    )


def test_protected_processing_policy_categories() -> None:
    assert issubclass(
        ProtectedFileProcessingPolicyError,
        FileProcessingPolicyError,
    )
    assert issubclass(
        ProtectedFileProcessingPolicyError,
        LifecycleError,
    )


def test_processing_policy_persistence_categories() -> None:
    assert issubclass(
        FileProcessingPolicyPersistenceError,
        FileProcessingPolicyError,
    )
    assert issubclass(
        FileProcessingPolicyPersistenceError,
        PersistenceError,
    )


def test_processing_policy_error_message_is_preserved() -> None:
    error = FileProcessingPolicyCodeConflictError(
        "The processing-policy code is already used."
    )

    assert str(error) == (
        "The processing-policy code is already used."
    )
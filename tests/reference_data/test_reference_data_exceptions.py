from app.exceptions import (
    ConfigurationError,
    ConflictError,
    NotFoundError,
    PersistenceError,
    ResponseConnectError,
)
from app.reference_data.exceptions import (
    DuplicateReferenceDatasetError,
    ReferenceDataConflictError,
    ReferenceDataError,
    ReferenceDataSynchronisationError,
    ReferenceDatasetNotFoundError,
)


def test_reference_data_error_inherits_from_platform_base() -> None:
    assert issubclass(
        ReferenceDataError,
        ResponseConnectError,
    )


def test_duplicate_reference_dataset_error_categories() -> None:
    assert issubclass(
        DuplicateReferenceDatasetError,
        ReferenceDataError,
    )
    assert issubclass(
        DuplicateReferenceDatasetError,
        ConfigurationError,
    )


def test_reference_dataset_not_found_error_categories() -> None:
    assert issubclass(
        ReferenceDatasetNotFoundError,
        ReferenceDataError,
    )
    assert issubclass(
        ReferenceDatasetNotFoundError,
        NotFoundError,
    )


def test_reference_data_conflict_error_categories() -> None:
    assert issubclass(
        ReferenceDataConflictError,
        ReferenceDataError,
    )
    assert issubclass(
        ReferenceDataConflictError,
        ConflictError,
    )


def test_reference_data_synchronisation_error_categories() -> None:
    assert issubclass(
        ReferenceDataSynchronisationError,
        ReferenceDataError,
    )
    assert issubclass(
        ReferenceDataSynchronisationError,
        PersistenceError,
    )


def test_reference_data_error_message_is_preserved() -> None:
    error = ReferenceDataConflictError(
        "The reference-data record conflicts "
        "with local data."
    )

    assert str(error) == (
        "The reference-data record conflicts "
        "with local data."
    )
"""Architecture tests for the public Event Journal API."""

from __future__ import annotations

import app.journal as journal


EXPECTED_PUBLIC_EXPORTS = {
    "InvalidJournalEntryError",
    "InvalidJournalReferenceError",
    "JournalEntryConflictError",
    "JournalEntryNotFoundError",
    "JournalEntryVisibilityError",
    "JournalError",
    "JournalPersistenceError",
    "JournalReferenceConflictError",
    "JournalReferenceNotFoundError",
    "JournalReferencePersistenceError",
    "JournalReferenceSpec",
    "JournalService",
}


FORBIDDEN_INTERNAL_EXPORTS = {
    "JournalEntry",
    "JournalReference",
    "JournalEntryService",
    "JournalReferenceService",
    "RecordJournalEntryCommand",
    "RegisterJournalReferenceCommand",
}


def test_journal_public_api_exports_expected_names() -> None:
    assert set(
        journal.__all__
    ) == EXPECTED_PUBLIC_EXPORTS


def test_journal_public_api_exports_resolve() -> None:
    missing_exports = [
        name
        for name in journal.__all__
        if not hasattr(
            journal,
            name,
        )
    ]

    assert not missing_exports, (
        "Journal public exports do not resolve:\n"
        + "\n".join(
            sorted(missing_exports)
        )
    )


def test_journal_public_api_contains_no_duplicates() -> None:
    assert len(
        journal.__all__
    ) == len(
        set(journal.__all__)
    )


def test_journal_public_api_contains_no_private_names() -> None:
    private_exports = [
        name
        for name in journal.__all__
        if name.startswith("_")
    ]

    assert not private_exports, (
        "Journal public API must not expose private names:\n"
        + "\n".join(
            sorted(private_exports)
        )
    )


def test_journal_public_api_does_not_export_internals() -> None:
    exposed_internals = (
        set(journal.__all__)
        & FORBIDDEN_INTERNAL_EXPORTS
    )

    assert not exposed_internals, (
        "Journal package root exposes internal implementation "
        "objects:\n"
        + "\n".join(
            sorted(exposed_internals)
        )
    )


def test_journal_service_is_available_from_package_root() -> None:
    from app.journal import JournalService

    assert JournalService is journal.JournalService


def test_journal_reference_spec_is_available_from_package_root(
) -> None:
    from app.journal import JournalReferenceSpec

    assert (
        JournalReferenceSpec
        is journal.JournalReferenceSpec
    )
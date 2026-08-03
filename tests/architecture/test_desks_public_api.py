"""Architecture tests for the public Desk package API."""

from __future__ import annotations

import app.desks as desks


EXPECTED_PUBLIC_EXPORTS = {
    "CreateDeskCommand",
    "Desk",
    "DeskConflictError",
    "DeskError",
    "DeskHierarchyError",
    "DeskLifecycleError",
    "DeskNotFoundError",
    "DeskPersistenceError",
    "DeskQueryService",
    "DeskService",
    "InvalidDeskError",
    "MoveDeskCommand",
    "UpdateDeskCommand",
}


def test_desks_public_api_exports_expected_names() -> None:
    assert set(
        desks.__all__
    ) == EXPECTED_PUBLIC_EXPORTS


def test_desks_public_api_exports_resolve() -> None:
    missing_exports = [
        name
        for name in desks.__all__
        if not hasattr(
            desks,
            name,
        )
    ]

    assert not missing_exports, (
        "Desk public exports do not resolve:\n"
        + "\n".join(
            sorted(missing_exports)
        )
    )


def test_desks_public_api_does_not_export_private_names() -> None:
    private_exports = [
        name
        for name in desks.__all__
        if name.startswith("_")
    ]

    assert not private_exports, (
        "Desk public API must not expose private names:\n"
        + "\n".join(
            sorted(private_exports)
        )
    )


def test_desks_public_api_contains_no_duplicates() -> None:
    assert len(
        desks.__all__
    ) == len(
        set(desks.__all__)
    )
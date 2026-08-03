"""Tests for Journal Reference validators."""

from __future__ import annotations

import uuid

import pytest

from app.journal.exceptions import (
    InvalidJournalReferenceError,
)
from app.journal.validators import (
    validate_reference_display_name,
    validate_reference_identity,
    validate_reference_stable_key,
    validate_reference_type,
)


@pytest.mark.parametrize(
    "value",
    [
        "user_account",
        "staff_member",
        "vehicle",
        "incident",
        "patient_journey",
        "event_medical_event",
        "system",
    ],
)
def test_validate_reference_type_accepts_valid_values(
    value: str,
) -> None:
    assert validate_reference_type(value) == value


def test_validate_reference_type_strips_whitespace() -> None:
    assert validate_reference_type(
        "  vehicle  "
    ) == "vehicle"


@pytest.mark.parametrize(
    "value",
    [
        "",
        "   ",
        "Vehicle",
        "staff member",
        "patient-journey",
        "incident.reference",
        "123_vehicle",
        "_vehicle",
    ],
)
def test_validate_reference_type_rejects_invalid_values(
    value: str,
) -> None:
    with pytest.raises(
        InvalidJournalReferenceError,
    ):
        validate_reference_type(value)


def test_validate_reference_type_rejects_long_value() -> None:
    value = "a" * 101

    with pytest.raises(
        InvalidJournalReferenceError,
        match="100",
    ):
        validate_reference_type(value)


def test_validate_reference_display_name_strips_whitespace(
) -> None:
    assert validate_reference_display_name(
        "  Vehicle A12  "
    ) == "Vehicle A12"


@pytest.mark.parametrize(
    "value",
    [
        "",
        "   ",
    ],
)
def test_validate_reference_display_name_requires_value(
    value: str,
) -> None:
    with pytest.raises(
        InvalidJournalReferenceError,
        match="display name",
    ):
        validate_reference_display_name(value)


def test_validate_reference_display_name_rejects_long_value(
) -> None:
    value = "A" * 256

    with pytest.raises(
        InvalidJournalReferenceError,
        match="255",
    ):
        validate_reference_display_name(value)


@pytest.mark.parametrize(
    "value",
    [
        "system",
        "scheduler:nightly",
        "integration:moodle",
        "api_client:external_dispatch",
        "worker:file_processor",
        "vehicle:a12",
        "event-2027",
    ],
)
def test_validate_reference_stable_key_accepts_valid_values(
    value: str,
) -> None:
    assert validate_reference_stable_key(value) == value


def test_validate_reference_stable_key_strips_whitespace(
) -> None:
    assert validate_reference_stable_key(
        "  scheduler:nightly  "
    ) == "scheduler:nightly"


def test_validate_reference_stable_key_returns_none_for_none(
) -> None:
    assert validate_reference_stable_key(
        None
    ) is None


def test_validate_reference_stable_key_returns_none_for_blank(
) -> None:
    assert validate_reference_stable_key(
        "   "
    ) is None


@pytest.mark.parametrize(
    "value",
    [
        "System",
        "scheduler nightly",
        "integration/moodle",
        "api.client",
        ":system",
        "_system",
        "-system",
        "system@example",
    ],
)
def test_validate_reference_stable_key_rejects_invalid_values(
    value: str,
) -> None:
    with pytest.raises(
        InvalidJournalReferenceError,
    ):
        validate_reference_stable_key(value)


def test_validate_reference_stable_key_rejects_long_value(
) -> None:
    value = "a" * 201

    with pytest.raises(
        InvalidJournalReferenceError,
        match="200",
    ):
        validate_reference_stable_key(value)


def test_validate_reference_identity_accepts_source_id(
) -> None:
    validate_reference_identity(
        source_id=uuid.uuid4(),
        stable_key=None,
    )


def test_validate_reference_identity_accepts_stable_key(
) -> None:
    validate_reference_identity(
        source_id=None,
        stable_key="system",
    )


def test_validate_reference_identity_accepts_both_values(
) -> None:
    validate_reference_identity(
        source_id=uuid.uuid4(),
        stable_key="vehicle:a12",
    )


def test_validate_reference_identity_requires_identity(
) -> None:
    with pytest.raises(
        InvalidJournalReferenceError,
        match="source ID or stable key",
    ):
        validate_reference_identity(
            source_id=None,
            stable_key=None,
        )
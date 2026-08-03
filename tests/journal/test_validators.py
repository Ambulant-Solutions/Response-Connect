"""Tests for Event Journal validators."""

import pytest

from app.journal.exceptions import (
    InvalidJournalEntryError,
)
from app.journal.validators import (
    validate_details,
    validate_event_code,
    validate_summary,
)


@pytest.mark.parametrize(
    "value",
    [
        "vehicle.arrived_on_scene",
        "staff.shift_signed_in",
        "authentication.login_failed",
        "desk.archived",
    ],
)
def test_validate_event_code_accepts_valid_codes(
    value: str,
) -> None:
    assert validate_event_code(value) == value


@pytest.mark.parametrize(
    "value",
    [
        "",
        "Vehicle.arrived",
        "vehicle",
        "vehicle-arrived.on_scene",
        "vehicle.arrived.on_scene",
        "vehicle.Arrived",
        "123.arrived",
    ],
)
def test_validate_event_code_rejects_invalid_codes(
    value: str,
) -> None:
    with pytest.raises(
        InvalidJournalEntryError,
    ):
        validate_event_code(value)


def test_validate_summary_strips_whitespace() -> None:
    assert validate_summary(
        "  Vehicle arrived on scene.  "
    ) == "Vehicle arrived on scene."


def test_validate_summary_requires_value() -> None:
    with pytest.raises(
        InvalidJournalEntryError,
    ):
        validate_summary("   ")


def test_validate_details_normalises_blank_value() -> None:
    assert validate_details("   ") is None


def test_validate_details_strips_whitespace() -> None:
    assert validate_details(
        "  Additional context.  "
    ) == "Additional context."
import pytest

from app.desks.exceptions import InvalidDeskError
from app.desks.validators import (
    normalise_desk_code,
    validate_desk_code,
    validate_desk_description,
    validate_desk_name,
)


def test_normalise_desk_code() -> None:
    assert normalise_desk_code(
        "  Devon_PTS  "
    ) == "devon_pts"


@pytest.mark.parametrize(
    "value",
    [
        "devon_pts",
        "company",
        "event_2027",
    ],
)
def test_validate_desk_code_accepts_valid_codes(
    value,
) -> None:
    assert validate_desk_code(value) == value


@pytest.mark.parametrize(
    "value",
    [
        "",
        "Devon PTS",
        "devon-pts",
        "123_desk",
        "desk.code",
    ],
)
def test_validate_desk_code_rejects_invalid_codes(
    value,
) -> None:
    with pytest.raises(
        InvalidDeskError
    ):
        validate_desk_code(value)


def test_validate_desk_name_strips_whitespace() -> None:
    assert validate_desk_name(
        "  Devon Patient Transport  "
    ) == "Devon Patient Transport"


def test_validate_desk_name_requires_value() -> None:
    with pytest.raises(
        InvalidDeskError
    ):
        validate_desk_name("   ")


def test_validate_desk_description_normalises_empty_value(
) -> None:
    assert validate_desk_description("   ") is None
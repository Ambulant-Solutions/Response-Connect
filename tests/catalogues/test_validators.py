import pytest

from app.catalogues import (
    InvalidCatalogueCodeError,
    validate_catalogue_code,
    validate_colour,
    validate_icon,
    validate_sort_order,
)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("file_type", "file_type"),
        ("Clinical_Grade", "clinical_grade"),
        ("  vehicle_type  ", "vehicle_type"),
        ("type2", "type2"),
    ],
)
def test_validate_catalogue_code_accepts_valid_codes(
    value: str,
    expected: str,
) -> None:
    assert (
        validate_catalogue_code(value)
        == expected
    )


@pytest.mark.parametrize(
    "value",
    [
        "",
        "2invalid",
        "invalid-code",
        "invalid code",
        "_invalid",
        "invalid.code",
    ],
)
def test_validate_catalogue_code_rejects_invalid_codes(
    value: str,
) -> None:
    with pytest.raises(
        InvalidCatalogueCodeError
    ):
        validate_catalogue_code(value)


def test_validate_colour_normalises_hex_value() -> None:
    assert validate_colour("#0ea5a0") == "#0EA5A0"


@pytest.mark.parametrize(
    "value",
    [
        "",
        "0EA5A0",
        "#FFF",
        "#GGGGGG",
    ],
)
def test_validate_colour_rejects_invalid_value(
    value: str,
) -> None:
    with pytest.raises(ValueError):
        validate_colour(value)


def test_validate_icon_accepts_iconify_identifier() -> None:
    assert (
        validate_icon("tabler:file")
        == "tabler:file"
    )


@pytest.mark.parametrize(
    "value",
    [
        "",
        "file",
        ":file",
        "tabler:",
    ],
)
def test_validate_icon_rejects_invalid_value(
    value: str,
) -> None:
    with pytest.raises(ValueError):
        validate_icon(value)


def test_validate_sort_order_accepts_zero() -> None:
    assert validate_sort_order(0) == 0


def test_validate_sort_order_rejects_negative_value() -> None:
    with pytest.raises(ValueError):
        validate_sort_order(-1)
from __future__ import annotations

from app.catalogues.constants import (
    CATALOGUE_CODE_PATTERN,
    MAX_CATALOGUE_CODE_LENGTH,
)
from app.catalogues.exceptions import InvalidCatalogueCodeError


def normalise_catalogue_code(value: str) -> str:
    """
    Normalise a catalogue code before validation.

    Normalisation is intentionally conservative. It does not silently convert
    arbitrary display names into stable codes.
    """

    return value.strip().lower()


def validate_catalogue_code(value: str) -> str:
    """
    Validate and return a normalised stable catalogue code.
    """

    code = normalise_catalogue_code(value)

    if not code:
        raise InvalidCatalogueCodeError(
            "A catalogue code is required."
        )

    if len(code) > MAX_CATALOGUE_CODE_LENGTH:
        raise InvalidCatalogueCodeError(
            f"Catalogue codes must not exceed "
            f"{MAX_CATALOGUE_CODE_LENGTH} characters."
        )

    if not CATALOGUE_CODE_PATTERN.fullmatch(code):
        raise InvalidCatalogueCodeError(
            "Catalogue codes must begin with a lowercase letter and "
            "contain only lowercase letters, numbers and underscores."
        )

    return code


def validate_sort_order(value: int) -> int:
    if value < 0:
        raise ValueError(
            "Catalogue sort order must be zero or greater."
        )

    return value


def validate_colour(value: str) -> str:
    colour = value.strip().upper()

    if len(colour) != 7 or not colour.startswith("#"):
        raise ValueError(
            "Catalogue colours must use a six-digit hexadecimal value."
        )

    try:
        int(colour[1:], 16)
    except ValueError as exc:
        raise ValueError(
            "Catalogue colours must use a valid hexadecimal value."
        ) from exc

    return colour


def validate_icon(value: str) -> str:
    icon = value.strip()

    if not icon:
        raise ValueError(
            "A catalogue icon is required."
        )

    if ":" not in icon:
        raise ValueError(
            "Catalogue icons must use a full Iconify identifier."
        )

    prefix, name = icon.split(":", 1)

    if not prefix or not name:
        raise ValueError(
            "Catalogue icons must use a valid Iconify identifier."
        )

    return icon
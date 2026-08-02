from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Pattern


PERMISSION_CODE_PATTERN = re.compile(
    r"^[a-z][a-z0-9_]*:[a-z][a-z0-9_]*$"
)

CATALOGUE_CODE_PATTERN = re.compile(
    r"^[a-z][a-z0-9_]*$"
)

DATASET_NAME_PATTERN = re.compile(
    r"^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$"
)

EVENT_CODE_PATTERN = re.compile(
    r"^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$"
)

CAPABILITY_CODE_PATTERN = re.compile(
    r"^[a-z][a-z0-9_]*$"
)


def find_invalid_values(
    values: Iterable[str],
    *,
    pattern: Pattern[str],
) -> list[str]:
    """
    Return unique values that do not match the supplied pattern.
    """

    return sorted({
        value
        for value in values
        if not pattern.fullmatch(value)
    })


def find_duplicate_values(
    values: Iterable[str],
) -> list[str]:
    """
    Return values that occur more than once.
    """

    value_list = list(values)

    return sorted({
        value
        for value in value_list
        if value_list.count(value) > 1
    })
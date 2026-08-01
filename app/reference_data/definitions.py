from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class ReferenceRecordDefinition:
    """
    One system-owned reference record.

    `values` contains the complete default values used when creating the
    record.

    `system_owned_fields` identifies values that Response Connect may update
    during future synchronisation.

    Fields omitted from `system_owned_fields` are treated as locally editable
    after initial creation.
    """

    code: str
    values: Mapping[str, Any]
    system_owned_fields: frozenset[str] = field(
        default_factory=frozenset
    )

    def __post_init__(self) -> None:
        if not self.code:
            raise ValueError(
                "Reference-data definitions require a stable code."
            )

        if "code" in self.values:
            raise ValueError(
                "The stable code must be supplied through the code field, "
                "not repeated inside values."
            )

        unknown_fields = (
            self.system_owned_fields
            - set(self.values.keys())
        )

        if unknown_fields:
            fields = ", ".join(
                sorted(unknown_fields)
            )

            raise ValueError(
                "System-owned fields must also exist in values: "
                f"{fields}."
            )


@dataclass(frozen=True)
class ReferenceDatasetDefinition:
    """
    A named collection of system reference records.
    """

    name: str
    records: tuple[ReferenceRecordDefinition, ...]

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError(
                "Reference datasets require a name."
            )

        codes = [
            record.code
            for record in self.records
        ]

        if len(codes) != len(set(codes)):
            raise ValueError(
                f"Reference dataset {self.name!r} contains "
                "duplicate stable codes."
            )
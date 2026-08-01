from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum

from app.reference_data.definitions import (
    ReferenceDatasetDefinition,
)


class ReferenceDataChangeType(StrEnum):
    CREATE = "create"
    UPDATE = "update"
    UNCHANGED = "unchanged"
    CONFLICT = "conflict"


@dataclass(frozen=True)
class ReferenceDataChange:
    dataset: str
    code: str
    change_type: ReferenceDataChangeType
    changed_fields: tuple[str, ...] = ()
    message: str | None = None


@dataclass
class ReferenceDataSynchronisationResult:
    dataset: str
    changes: list[ReferenceDataChange] = field(
        default_factory=list
    )

    @property
    def created_count(self) -> int:
        return sum(
            change.change_type
            is ReferenceDataChangeType.CREATE
            for change in self.changes
        )

    @property
    def updated_count(self) -> int:
        return sum(
            change.change_type
            is ReferenceDataChangeType.UPDATE
            for change in self.changes
        )

    @property
    def unchanged_count(self) -> int:
        return sum(
            change.change_type
            is ReferenceDataChangeType.UNCHANGED
            for change in self.changes
        )

    @property
    def conflict_count(self) -> int:
        return sum(
            change.change_type
            is ReferenceDataChangeType.CONFLICT
            for change in self.changes
        )


class ReferenceDatasetSynchroniser(ABC):
    """
    Model-specific adapter for synchronising one reference dataset.
    """

    dataset: ReferenceDatasetDefinition

    @abstractmethod
    def synchronise(
        self,
        *,
        dry_run: bool = False,
    ) -> ReferenceDataSynchronisationResult:
        """
        Synchronise this dataset and return a structured result.
        """
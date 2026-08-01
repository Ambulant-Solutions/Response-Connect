from __future__ import annotations

from collections.abc import Iterable

from app.reference_data.exceptions import (
    DuplicateReferenceDatasetError,
    ReferenceDatasetNotFoundError,
)
from app.reference_data.synchroniser import (
    ReferenceDatasetSynchroniser,
)


class ReferenceDataRegistry:
    """
    Registry of available reference-data dataset synchronisers.
    """

    def __init__(self) -> None:
        self._synchronisers: dict[
            str,
            ReferenceDatasetSynchroniser,
        ] = {}

    def register(
        self,
        synchroniser: ReferenceDatasetSynchroniser,
    ) -> None:
        dataset_name = synchroniser.dataset.name

        if dataset_name in self._synchronisers:
            raise DuplicateReferenceDatasetError(
                "A reference-data synchroniser is already "
                f"registered for {dataset_name!r}."
            )

        self._synchronisers[
            dataset_name
        ] = synchroniser

    def get(
        self,
        dataset_name: str,
    ) -> ReferenceDatasetSynchroniser:
        try:
            return self._synchronisers[
                dataset_name
            ]
        except KeyError as exc:
            raise ReferenceDatasetNotFoundError(
                f"Reference dataset {dataset_name!r} "
                "is not registered."
            ) from exc

    def list_names(self) -> list[str]:
        return sorted(self._synchronisers)

    def iter_synchronisers(
        self,
    ) -> Iterable[ReferenceDatasetSynchroniser]:
        for dataset_name in self.list_names():
            yield self._synchronisers[
                dataset_name
            ]
from flask import current_app

from app.reference_data.definitions import (
    ReferenceDatasetDefinition,
    ReferenceRecordDefinition,
)
from app.reference_data.registry import (
    ReferenceDataRegistry,
)
from app.reference_data.synchroniser import (
    ReferenceDataChange,
    ReferenceDataChangeType,
    ReferenceDataSynchronisationResult,
    ReferenceDatasetSynchroniser,
)


_REGISTRY_EXTENSION_KEY = "response_connect_reference_data"


def init_reference_data(
    app,
) -> ReferenceDataRegistry:
    """
    Initialise the application-wide reference-data registry.
    """

    registry = ReferenceDataRegistry()

    app.extensions[
        _REGISTRY_EXTENSION_KEY
    ] = registry

    return registry


def get_reference_data_registry(
) -> ReferenceDataRegistry:
    """
    Return the registry attached to the current Flask application.
    """

    try:
        return current_app.extensions[
            _REGISTRY_EXTENSION_KEY
        ]
    except KeyError as exc:
        raise RuntimeError(
            "The reference-data registry has not been "
            "initialised for this application."
        ) from exc


__all__ = [
    "ReferenceDataChange",
    "ReferenceDataChangeType",
    "ReferenceDataRegistry",
    "ReferenceDataSynchronisationResult",
    "ReferenceDatasetDefinition",
    "ReferenceDatasetSynchroniser",
    "ReferenceRecordDefinition",
    "get_reference_data_registry",
    "init_reference_data",
]
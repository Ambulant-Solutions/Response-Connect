from __future__ import annotations

import re

from app import create_app
from app.reference_data import (
    ReferenceDatasetSynchroniser,
    get_reference_data_registry,
)


DATASET_NAME_PATTERN = re.compile(
    r"^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$"
)


def test_reference_data_dataset_names_are_unique() -> None:
    app = create_app(
        {
            "TESTING": True,
        }
    )

    with app.app_context():
        registry = get_reference_data_registry()

        dataset_names = [
            synchroniser.dataset.name
            for synchroniser
            in registry.iter_synchronisers()
        ]

    assert len(dataset_names) == len(
        set(dataset_names)
    ), (
        "Reference-data dataset names must be unique. "
        f"Registered names: {dataset_names!r}"
    )


def test_reference_data_dataset_names_are_valid() -> None:
    app = create_app(
        {
            "TESTING": True,
        }
    )

    with app.app_context():
        registry = get_reference_data_registry()

        dataset_names = registry.list_names()

    invalid_names = [
        dataset_name
        for dataset_name in dataset_names
        if not DATASET_NAME_PATTERN.fullmatch(
            dataset_name
        )
    ]

    assert not invalid_names, (
        "Reference-data dataset names must use the "
        "'module.dataset_name' format with lowercase "
        "snake_case components:\n"
        + "\n".join(
            sorted(invalid_names)
        )
    )


def test_registered_datasets_have_synchronisers() -> None:
    app = create_app(
        {
            "TESTING": True,
        }
    )

    with app.app_context():
        registry = get_reference_data_registry()

        missing_synchronisers: list[str] = []

        for dataset_name in registry.list_names():
            synchroniser = registry.get(
                dataset_name
            )

            if synchroniser is None:
                missing_synchronisers.append(
                    dataset_name
                )

    assert not missing_synchronisers, (
        "Every registered reference-data dataset "
        "must have a synchroniser:\n"
        + "\n".join(
            sorted(missing_synchronisers)
        )
    )


def test_registered_synchronisers_use_platform_base() -> None:
    app = create_app(
        {
            "TESTING": True,
        }
    )

    with app.app_context():
        registry = get_reference_data_registry()

        invalid_synchronisers: list[str] = []

        for synchroniser in (
            registry.iter_synchronisers()
        ):
            if not isinstance(
                synchroniser,
                ReferenceDatasetSynchroniser,
            ):
                invalid_synchronisers.append(
                    (
                        f"{synchroniser.dataset.name}: "
                        f"{type(synchroniser).__module__}."
                        f"{type(synchroniser).__name__}"
                    )
                )

    assert not invalid_synchronisers, (
        "Reference-data synchronisers must inherit "
        "from ReferenceDatasetSynchroniser:\n"
        + "\n".join(
            sorted(invalid_synchronisers)
        )
    )


def test_registered_dataset_codes_are_unique() -> None:
    app = create_app(
        {
            "TESTING": True,
        }
    )

    with app.app_context():
        registry = get_reference_data_registry()

        violations: list[str] = []

        for synchroniser in (
            registry.iter_synchronisers()
        ):
            dataset = synchroniser.dataset

            codes = [
                record.code
                for record in dataset.records
            ]

            duplicate_codes = sorted({
                code
                for code in codes
                if codes.count(code) > 1
            })

            for code in duplicate_codes:
                violations.append(
                    f"{dataset.name}: {code}"
                )

    assert not violations, (
        "Reference-data record codes must be unique "
        "within each dataset:\n"
        + "\n".join(
            violations
        )
    )


def test_registered_dataset_codes_are_valid() -> None:
    app = create_app(
        {
            "TESTING": True,
        }
    )

    with app.app_context():
        registry = get_reference_data_registry()

        violations: list[str] = []

        code_pattern = re.compile(
            r"^[a-z][a-z0-9_]*$"
        )

        for synchroniser in (
            registry.iter_synchronisers()
        ):
            dataset = synchroniser.dataset

            for record in dataset.records:
                if not code_pattern.fullmatch(
                    record.code
                ):
                    violations.append(
                        f"{dataset.name}: {record.code}"
                    )

    assert not violations, (
        "Reference-data record codes must use "
        "lowercase snake_case:\n"
        + "\n".join(
            sorted(violations)
        )
    )
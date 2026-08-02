from __future__ import annotations

import ast
from pathlib import Path

from app import create_app
from app.blueprints.auth.models import Permission
from app.extensions import db
from app.reference_data import (
    get_reference_data_registry,
)
from tests.architecture.helpers import (
    CATALOGUE_CODE_PATTERN,
    DATASET_NAME_PATTERN,
    PERMISSION_CODE_PATTERN,
    find_duplicate_values,
    find_invalid_values,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = PROJECT_ROOT / "app"


def collect_permission_codes_from_database(
) -> list[str]:
    return list(
        db.session.scalars(
            db.select(Permission.name)
        ).all()
    )


def collect_permission_codes_from_source(
) -> list[str]:
    """
    Extract literal permission codes used in decorators and checks.

    This catches invalid codes even when the permission catalogue has not
    yet been synchronised into the test database.
    """

    permission_codes: set[str] = set()

    function_names = {
        "permission_required",
        "any_permission_required",
        "has_permission",
    }

    for file_path in APP_ROOT.rglob("*.py"):
        tree = ast.parse(
            file_path.read_text(
                encoding="utf-8"
            ),
            filename=str(file_path),
        )

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue

            function_name: str | None = None

            if isinstance(node.func, ast.Name):
                function_name = node.func.id

            elif isinstance(
                node.func,
                ast.Attribute,
            ):
                function_name = node.func.attr

            if function_name not in function_names:
                continue

            for argument in node.args:
                if (
                    isinstance(argument, ast.Constant)
                    and isinstance(argument.value, str)
                ):
                    permission_codes.add(
                        argument.value
                    )

    return sorted(permission_codes)


def test_permission_codes_use_valid_format(
    app,
) -> None:
    with app.app_context():
        permission_codes = set(
            collect_permission_codes_from_database()
        )

        permission_codes.update(
            collect_permission_codes_from_source()
        )

    invalid_codes = find_invalid_values(
        permission_codes,
        pattern=PERMISSION_CODE_PATTERN,
    )

    assert not invalid_codes, (
        "Permission codes must use the "
        "'domain:action' lowercase format:\n"
        + "\n".join(
            repr(code)
            for code in invalid_codes
        )
    )



def test_permission_codes_are_unique(
    app,
) -> None:
    with app.app_context():
        database_codes = (
            collect_permission_codes_from_database()
        )

    duplicate_codes = find_duplicate_values(
        database_codes
    )

    assert not duplicate_codes, (
        "Permission codes must be unique:\n"
        + "\n".join(duplicate_codes)
    )


def test_reference_dataset_names_use_valid_format(
) -> None:
    app = create_app(
        {
            "TESTING": True,
        }
    )

    with app.app_context():
        registry = get_reference_data_registry()
        dataset_names = registry.list_names()

    invalid_names = find_invalid_values(
        dataset_names,
        pattern=DATASET_NAME_PATTERN,
    )

    assert not invalid_names, (
        "Reference-data dataset names must use "
        "'module.dataset_name' format:\n"
        + "\n".join(invalid_names)
    )


def test_reference_record_codes_use_valid_format(
) -> None:
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
            invalid_codes = find_invalid_values(
                (
                    record.code
                    for record
                    in synchroniser.dataset.records
                ),
                pattern=CATALOGUE_CODE_PATTERN,
            )

            violations.extend(
                (
                    f"{synchroniser.dataset.name}: "
                    f"{code}"
                )
                for code in invalid_codes
            )

    assert not violations, (
        "Reference-data record codes must use "
        "lowercase snake_case:\n"
        + "\n".join(sorted(violations))
    )
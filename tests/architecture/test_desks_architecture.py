"""Architecture safeguards for the Desk platform."""

from __future__ import annotations

import ast
from pathlib import Path

from app.desks.exceptions import DeskError
from app.exceptions import ResponseConnectError


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DESKS_PACKAGE = PROJECT_ROOT / "app" / "desks"


def imported_modules(
    path: Path,
) -> set[str]:
    tree = ast.parse(
        path.read_text(
            encoding="utf-8"
        )
    )

    modules: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(
                alias.name
                for alias in node.names
            )

        if isinstance(node, ast.ImportFrom):
            if node.module:
                modules.add(
                    node.module
                )

    return modules


def test_desk_services_do_not_import_routes_or_templates(
) -> None:
    violations: list[str] = []

    for filename in (
        "services.py",
        "queries.py",
    ):
        path = DESKS_PACKAGE / filename

        for module in imported_modules(path):
            if (
                ".routes" in module
                or ".templates" in module
                or module.endswith(".routes")
            ):
                violations.append(
                    f"{filename}: {module}"
                )

    assert not violations, (
        "Desk services and queries must not import "
        "routes or templates:\n"
        + "\n".join(
            sorted(violations)
        )
    )


def test_desk_models_do_not_import_services_or_queries(
) -> None:
    modules = imported_modules(
        DESKS_PACKAGE / "models.py"
    )

    violations = [
        module
        for module in modules
        if module in {
            "app.desks.services",
            "app.desks.queries",
        }
    ]

    assert not violations, (
        "Desk models must not depend on Desk "
        "services or queries:\n"
        + "\n".join(
            sorted(violations)
        )
    )


def test_desk_exception_base_uses_platform_hierarchy(
) -> None:
    assert issubclass(
        DeskError,
        ResponseConnectError,
    )
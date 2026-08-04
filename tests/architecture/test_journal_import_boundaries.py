"""Import-boundary safeguards for the Event Journal package."""

from __future__ import annotations

import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = PROJECT_ROOT / "app"
JOURNAL_PACKAGE = APP_ROOT / "journal"


FORBIDDEN_JOURNAL_MODULES = {
    "app.journal.commands",
    "app.journal.constants",
    "app.journal.models",
    "app.journal.queries",
    "app.journal.reference_data",
    "app.journal.service",
    "app.journal.services",
    "app.journal.validators",
}


# SQLAlchemy must import model modules during application startup so their
# tables are registered in metadata. This is an infrastructure concern,
# not a business-module dependency.
ALLOWED_INTERNAL_IMPORTERS = {
    APP_ROOT / "__init__.py",
}


def application_python_files() -> list[Path]:
    """Return application Python files outside the Journal package."""

    return sorted(
        path
        for path in APP_ROOT.rglob("*.py")
        if not path.is_relative_to(
            JOURNAL_PACKAGE
        )
    )


def imported_modules(
    path: Path,
) -> list[tuple[int, str]]:
    """Return imported module names with source line numbers."""

    tree = ast.parse(
        path.read_text(
            encoding="utf-8"
        ),
        filename=str(path),
    )

    imports: list[tuple[int, str]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(
                (
                    node.lineno,
                    alias.name,
                )
                for alias in node.names
            )

        elif isinstance(node, ast.ImportFrom):
            if node.module is not None:
                imports.append(
                    (
                        node.lineno,
                        node.module,
                    )
                )

    return imports


def is_forbidden_journal_import(
    module: str,
) -> bool:
    """Return whether an import bypasses the Journal public API."""

    return any(
        module == forbidden
        or module.startswith(
            f"{forbidden}."
        )
        for forbidden in FORBIDDEN_JOURNAL_MODULES
    )


def test_application_modules_do_not_import_journal_internals(
) -> None:
    violations: list[str] = []

    for path in application_python_files():
        if path in ALLOWED_INTERNAL_IMPORTERS:
            continue

        for line_number, module in imported_modules(path):
            if is_forbidden_journal_import(module):
                relative_path = path.relative_to(
                    PROJECT_ROOT
                )

                violations.append(
                    f"{relative_path}:{line_number}: "
                    f"imports {module}"
                )

    assert not violations, (
        "Application modules must use the public Journal API:\n"
        "\n".join(
            sorted(violations)
        )
        + "\n\nUse:\n"
        "    from app.journal import JournalService\n"
        "or import Journal exceptions from app.journal.\n"
        "\nDo not import Journal commands, models, validators, "
        "or implementation services."
    )


def test_journal_internal_module_list_is_complete() -> None:
    """
    Ensure newly added Journal implementation modules are classified.

    This forces an explicit architecture decision whenever another module
    is introduced beneath app/journal.
    """

    ignored_modules = {
        "app.journal",
        "app.journal.exceptions",
    }

    def module_name_from_path(
        path: Path,
    ) -> str:
        relative_path = path.relative_to(
            APP_ROOT
        ).with_suffix("")

        parts = list(
            relative_path.parts
        )

        if parts[-1] == "__init__":
            parts.pop()

        return "app." + ".".join(
            parts
        )

    discovered_modules = {
        module_name_from_path(path)
        for path in JOURNAL_PACKAGE.glob("*.py")
    }

    unclassified_modules = (
        discovered_modules
        - FORBIDDEN_JOURNAL_MODULES
        - ignored_modules
    )

    assert not unclassified_modules, (
        "Journal modules are not classified as public or internal:\n"
        + "\n".join(
            sorted(unclassified_modules)
        )
        + "\n\nAdd each module to the public exception list or "
        "FORBIDDEN_JOURNAL_MODULES."
    )
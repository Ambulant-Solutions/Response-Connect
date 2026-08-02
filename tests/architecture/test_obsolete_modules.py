from __future__ import annotations

import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = PROJECT_ROOT / "app"


OBSOLETE_MODULES = {
    "app.blueprints.org.hr.job_positions.routes":
        "Use app.blueprints.org.settings.workforce.routes instead.",
}


def iter_python_files():
    yield from APP_ROOT.rglob("*.py")


def extract_imports(
    file_path: Path,
) -> set[str]:
    tree = ast.parse(
        file_path.read_text(
            encoding="utf-8"
        ),
        filename=str(file_path),
    )

    imports: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(
                alias.name
                for alias in node.names
            )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            if node.module:
                imports.add(node.module)

    return imports


def test_no_obsolete_modules_are_imported() -> None:
    violations: list[str] = []

    for file_path in iter_python_files():
        imports = extract_imports(file_path)

        for imported_module in imports:
            for obsolete_module, replacement in (
                OBSOLETE_MODULES.items()
            ):
                if imported_module.startswith(
                    obsolete_module
                ):
                    relative_path = (
                        file_path.relative_to(
                            PROJECT_ROOT
                        )
                    )

                    violations.append(
                        f"{relative_path}\n"
                        f"  imports: {obsolete_module}\n"
                        f"  replacement: {replacement}"
                    )

    assert not violations, (
        "Obsolete modules must not be imported:\n\n"
        + "\n\n".join(
            sorted(violations)
        )
    )
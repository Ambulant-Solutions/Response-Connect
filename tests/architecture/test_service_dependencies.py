from __future__ import annotations

import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = PROJECT_ROOT / "app"


def iter_service_files():
    """
    Yield Python modules that represent service-layer code.
    """

    patterns = (
        "**/services.py",
        "**/service.py",
        "**/*_service.py",
        "**/*_services.py",
    )

    seen: set[Path] = set()

    for pattern in patterns:
        for file_path in APP_ROOT.glob(pattern):
            if file_path in seen:
                continue

            seen.add(file_path)
            yield file_path


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


def is_route_import(
    imported_module: str,
) -> bool:
    module_parts = imported_module.split(".")

    return (
        "routes" in module_parts
        or imported_module.endswith("_routes")
        or imported_module.endswith(".route")
    )


def test_service_modules_do_not_import_route_modules(
) -> None:
    violations: list[str] = []

    for file_path in iter_service_files():
        imports = extract_imports(file_path)

        for imported_module in imports:
            if not is_route_import(imported_module):
                continue

            relative_path = file_path.relative_to(
                PROJECT_ROOT
            )

            violations.append(
                f"{relative_path}: "
                f"{imported_module}"
            )

    assert not violations, (
        "Service modules must not import HTTP route "
        "modules:\n"
        + "\n".join(
            sorted(violations)
        )
    )
from __future__ import annotations

import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = PROJECT_ROOT / "app"

PLATFORM_PACKAGES = (
    "catalogues",
    "files",
    "reference_data",
)

FORBIDDEN_IMPORT_PREFIXES = (
    "app.blueprints.org",
    "app.blueprints.personal",
    "app.blueprints.jobs",
    "app.blueprints.job_application",
    "app.blueprints.external",
)


def iter_python_files(
    package_name: str,
):
    package_path = APP_ROOT / package_name

    yield from package_path.rglob("*.py")


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


def test_platform_packages_do_not_import_business_blueprints(
) -> None:
    violations: list[str] = []

    for package_name in PLATFORM_PACKAGES:
        for file_path in iter_python_files(
            package_name
        ):
            imports = extract_imports(
                file_path
            )

            for imported_module in imports:
                if imported_module.startswith(
                    FORBIDDEN_IMPORT_PREFIXES
                ):
                    relative_path = (
                        file_path.relative_to(
                            PROJECT_ROOT
                        )
                    )

                    violations.append(
                        f"{relative_path}: "
                        f"{imported_module}"
                    )

    assert not violations, (
        "Platform packages must not import "
        "business blueprints:\n"
        + "\n".join(
            sorted(violations)
        )
    )
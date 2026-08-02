from __future__ import annotations

import importlib
from types import ModuleType


PUBLIC_PACKAGES = (
    "app.catalogues",
    "app.files",
    "app.reference_data",
)


def import_public_package(
    package_name: str,
) -> ModuleType:
    return importlib.import_module(
        package_name
    )


def get_public_exports(
    package: ModuleType,
) -> tuple[str, ...]:
    exports = getattr(
        package,
        "__all__",
        None,
    )

    assert exports is not None, (
        f"{package.__name__} must define __all__ "
        "to declare its public API."
    )

    assert isinstance(
        exports,
        (list, tuple),
    ), (
        f"{package.__name__}.__all__ must be "
        "a list or tuple."
    )

    return tuple(exports)


def test_public_packages_import_successfully() -> None:
    failures: list[str] = []

    for package_name in PUBLIC_PACKAGES:
        try:
            import_public_package(
                package_name
            )
        except Exception as exc:
            failures.append(
                f"{package_name}: "
                f"{type(exc).__name__}: {exc}"
            )

    assert not failures, (
        "Public packages must import without "
        "raising exceptions:\n"
        + "\n".join(
            sorted(failures)
        )
    )


def test_public_packages_define_exports() -> None:
    failures: list[str] = []

    for package_name in PUBLIC_PACKAGES:
        package = import_public_package(
            package_name
        )

        exports = getattr(
            package,
            "__all__",
            None,
        )

        if exports is None:
            failures.append(
                f"{package_name}: missing __all__"
            )

    assert not failures, (
        "Public packages must define __all__:\n"
        + "\n".join(
            sorted(failures)
        )
    )


def test_public_exports_are_unique() -> None:
    violations: list[str] = []

    for package_name in PUBLIC_PACKAGES:
        package = import_public_package(
            package_name
        )

        exports = get_public_exports(
            package
        )

        duplicate_names = sorted({
            name
            for name in exports
            if exports.count(name) > 1
        })

        for name in duplicate_names:
            violations.append(
                f"{package_name}: {name}"
            )

    assert not violations, (
        "Public package exports must not contain "
        "duplicate names:\n"
        + "\n".join(
            violations
        )
    )


def test_public_exports_resolve() -> None:
    violations: list[str] = []

    for package_name in PUBLIC_PACKAGES:
        package = import_public_package(
            package_name
        )

        for export_name in get_public_exports(
            package
        ):
            if not hasattr(
                package,
                export_name,
            ):
                violations.append(
                    f"{package_name}: "
                    f"{export_name}"
                )

    assert not violations, (
        "Every name declared in __all__ must "
        "exist on the public package:\n"
        + "\n".join(
            sorted(violations)
        )
    )


def test_public_exports_use_valid_names() -> None:
    violations: list[str] = []

    for package_name in PUBLIC_PACKAGES:
        package = import_public_package(
            package_name
        )

        for export_name in get_public_exports(
            package
        ):
            if not export_name.isidentifier():
                violations.append(
                    f"{package_name}: "
                    f"{export_name!r}"
                )

    assert not violations, (
        "Public export names must be valid "
        "Python identifiers:\n"
        + "\n".join(
            sorted(violations)
        )
    )


def test_public_exports_do_not_include_private_names(
) -> None:
    violations: list[str] = []

    for package_name in PUBLIC_PACKAGES:
        package = import_public_package(
            package_name
        )

        for export_name in get_public_exports(
            package
        ):
            if export_name.startswith("_"):
                violations.append(
                    f"{package_name}: "
                    f"{export_name}"
                )

    assert not violations, (
        "Public package exports must not expose "
        "private names:\n"
        + "\n".join(
            sorted(violations)
        )
    )
from __future__ import annotations

import inspect
from types import ModuleType

from app import exceptions as platform_exceptions
from app.catalogues import exceptions as catalogue_exceptions
from app.exceptions import ResponseConnectError
from app.files import exceptions as file_exceptions
from app.reference_data import (
    exceptions as reference_data_exceptions,
)


EXCEPTION_MODULES: tuple[ModuleType, ...] = (
    catalogue_exceptions,
    file_exceptions,
    reference_data_exceptions,
)


PLATFORM_EXCEPTION_CLASSES = frozenset(
    exception_class
    for _, exception_class in inspect.getmembers(
        platform_exceptions,
        inspect.isclass,
    )
    if issubclass(
        exception_class,
        ResponseConnectError,
    )
)


def iter_module_exception_classes(
    module: ModuleType,
) -> list[type[BaseException]]:
    """
    Return exception classes defined directly by the supplied module.

    Imported platform exception categories are excluded.
    """

    return [
        exception_class
        for _, exception_class in inspect.getmembers(
            module,
            inspect.isclass,
        )
        if exception_class.__module__ == module.__name__
        and issubclass(
            exception_class,
            BaseException,
        )
    ]


def test_module_exceptions_inherit_from_response_connect_error(
) -> None:
    violations: list[str] = []

    for module in EXCEPTION_MODULES:
        for exception_class in (
            iter_module_exception_classes(module)
        ):
            if not issubclass(
                exception_class,
                ResponseConnectError,
            ):
                violations.append(
                    f"{module.__name__}."
                    f"{exception_class.__name__}"
                )

    assert not violations, (
        "Module-specific exceptions must inherit "
        "from ResponseConnectError:\n"
        + "\n".join(
            sorted(violations)
        )
    )


def test_module_exception_names_end_with_error(
) -> None:
    violations: list[str] = []

    for module in EXCEPTION_MODULES:
        for exception_class in (
            iter_module_exception_classes(module)
        ):
            if not exception_class.__name__.endswith(
                "Error"
            ):
                violations.append(
                    f"{module.__name__}."
                    f"{exception_class.__name__}"
                )

    assert not violations, (
        "Module-specific exception names must end "
        "with 'Error':\n"
        + "\n".join(
            sorted(violations)
        )
    )


def test_module_exception_classes_are_not_platform_categories(
) -> None:
    """
    Ensure module exception files define their own domain exceptions rather
    than aliasing platform categories as module-specific exceptions.
    """

    violations: list[str] = []

    for module in EXCEPTION_MODULES:
        for exception_class in (
            iter_module_exception_classes(module)
        ):
            if exception_class in PLATFORM_EXCEPTION_CLASSES:
                violations.append(
                    f"{module.__name__}."
                    f"{exception_class.__name__}"
                )

    assert not violations, (
        "Module exception classes must be distinct "
        "domain-specific classes:\n"
        + "\n".join(
            sorted(violations)
        )
    )


def test_module_exception_files_define_exceptions(
) -> None:
    empty_modules = [
        module.__name__
        for module in EXCEPTION_MODULES
        if not iter_module_exception_classes(module)
    ]

    assert not empty_modules, (
        "Registered module exception files must "
        "define at least one custom exception:\n"
        + "\n".join(
            sorted(empty_modules)
        )
    )
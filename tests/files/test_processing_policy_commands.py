from dataclasses import FrozenInstanceError

import pytest

from app.files.commands import (
    CreateFileProcessingPolicyCommand,
    ReplaceFileProcessingRulesCommand,
)
from app.files.models import FileCategory


def test_create_command_is_immutable() -> None:
    command = CreateFileProcessingPolicyCommand(
        code="test_policy",
        name="Test Policy",
        category=FileCategory.GENERIC,
        max_size_bytes=1024,
        extensions=("bin",),
        mime_types=(
            "application/octet-stream",
        ),
    )

    with pytest.raises(FrozenInstanceError):
        command.name = "Changed"  # type: ignore[misc]


def test_replace_rules_command_accepts_tuples() -> None:
    command = ReplaceFileProcessingRulesCommand(
        extensions=("pdf",),
        mime_types=("application/pdf",),
    )

    assert tuple(command.extensions) == ("pdf",)
    assert tuple(command.mime_types) == (
        "application/pdf",
    )
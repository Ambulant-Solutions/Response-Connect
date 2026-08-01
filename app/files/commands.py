from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from app.files.models import FileCategory


@dataclass(frozen=True)
class CreateFileProcessingPolicyCommand:
    """Input required to create a file-processing policy."""

    code: str
    name: str
    category: FileCategory | str
    max_size_bytes: int
    extensions: Iterable[str]
    mime_types: Iterable[str]

    description: str | None = None
    icon: str = "tabler:file-settings"
    colour: str = "#334155"
    sort_order: int = 0

    requires_virus_scan: bool = True
    generate_thumbnail: bool = False
    generate_preview: bool = False
    enable_ocr: bool = False
    optimise_image: bool = False
    extract_metadata: bool = False

    is_system: bool = False
    is_active: bool = True


@dataclass(frozen=True)
class UpdateFileProcessingPolicyCommand:
    """Editable values for an existing file-processing policy."""

    name: str
    category: FileCategory | str
    max_size_bytes: int
    extensions: Iterable[str]
    mime_types: Iterable[str]

    description: str | None
    icon: str
    colour: str
    sort_order: int

    requires_virus_scan: bool
    generate_thumbnail: bool
    generate_preview: bool
    enable_ocr: bool
    optimise_image: bool
    extract_metadata: bool


@dataclass(frozen=True)
class ReplaceFileProcessingRulesCommand:
    """Replacement extension and MIME-type rules for a policy."""

    extensions: Iterable[str]
    mime_types: Iterable[str]
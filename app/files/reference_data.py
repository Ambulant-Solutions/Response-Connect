from __future__ import annotations

from app.files.models import FileCategory
from app.reference_data import (
    ReferenceDatasetDefinition,
    ReferenceRecordDefinition,
)


FILE_PROCESSING_POLICY_DATASET = (
    ReferenceDatasetDefinition(
        name="files.processing_policies",
        records=(
            ReferenceRecordDefinition(
                code="generic_binary",
                values={
                    "name": "Generic Binary File",
                    "description": (
                        "Fallback policy for binary files that do not "
                        "require specialised processing."
                    ),
                    "icon": "tabler:file-binary",
                    "colour": "#334155",
                    "sort_order": 100,
                    "is_active": True,
                    "category": FileCategory.GENERIC.value,
                    "max_size_bytes": 25 * 1024 * 1024,
                    "requires_virus_scan": True,
                    "generate_thumbnail": False,
                    "generate_preview": False,
                    "enable_ocr": False,
                    "optimise_image": False,
                    "extract_metadata": False,
                    "extensions": (
                        "bin",
                        "dat",
                    ),
                    "mime_types": (
                        "application/octet-stream",
                    ),
                },
                system_owned_fields=frozenset({
                    "category",
                    "max_size_bytes",
                    "requires_virus_scan",
                    "generate_thumbnail",
                    "generate_preview",
                    "enable_ocr",
                    "optimise_image",
                    "extract_metadata",
                    "extensions",
                    "mime_types",
                }),
            ),
            ReferenceRecordDefinition(
                code="pdf_document",
                values={
                    "name": "PDF Document",
                    "description": (
                        "Standard policy for uploaded PDF documents."
                    ),
                    "icon": "tabler:file-type-pdf",
                    "colour": "#6366F1",
                    "sort_order": 10,
                    "is_active": True,
                    "category": FileCategory.DOCUMENT.value,
                    "max_size_bytes": 25 * 1024 * 1024,
                    "requires_virus_scan": True,
                    "generate_thumbnail": False,
                    "generate_preview": True,
                    "enable_ocr": False,
                    "optimise_image": False,
                    "extract_metadata": True,
                    "extensions": ("pdf",),
                    "mime_types": (
                        "application/pdf",
                    ),
                },
                system_owned_fields=frozenset({
                    "category",
                    "max_size_bytes",
                    "requires_virus_scan",
                    "generate_thumbnail",
                    "generate_preview",
                    "enable_ocr",
                    "optimise_image",
                    "extract_metadata",
                    "extensions",
                    "mime_types",
                }),
            ),
            ReferenceRecordDefinition(
                code="standard_image",
                values={
                    "name": "Standard Image",
                    "description": (
                        "General policy for ordinary uploaded images."
                    ),
                    "icon": "tabler:photo",
                    "colour": "#0EA5A0",
                    "sort_order": 20,
                    "is_active": True,
                    "category": FileCategory.IMAGE.value,
                    "max_size_bytes": 10 * 1024 * 1024,
                    "requires_virus_scan": True,
                    "generate_thumbnail": True,
                    "generate_preview": True,
                    "enable_ocr": False,
                    "optimise_image": True,
                    "extract_metadata": True,
                    "extensions": (
                        "jpg",
                        "jpeg",
                        "png",
                        "webp",
                    ),
                    "mime_types": (
                        "image/jpeg",
                        "image/png",
                        "image/webp",
                    ),
                },
                system_owned_fields=frozenset({
                    "category",
                    "max_size_bytes",
                    "requires_virus_scan",
                    "generate_thumbnail",
                    "generate_preview",
                    "enable_ocr",
                    "optimise_image",
                    "extract_metadata",
                    "extensions",
                    "mime_types",
                }),
            ),
            ReferenceRecordDefinition(
                code="profile_photo",
                values={
                    "name": "Profile Photograph",
                    "description": (
                        "Policy for small profile and identity images."
                    ),
                    "icon": "tabler:user-square-rounded",
                    "colour": "#0EA5A0",
                    "sort_order": 30,
                    "is_active": True,
                    "category": FileCategory.IMAGE.value,
                    "max_size_bytes": 5 * 1024 * 1024,
                    "requires_virus_scan": True,
                    "generate_thumbnail": True,
                    "generate_preview": True,
                    "enable_ocr": False,
                    "optimise_image": True,
                    "extract_metadata": True,
                    "extensions": (
                        "jpg",
                        "jpeg",
                        "png",
                        "webp",
                    ),
                    "mime_types": (
                        "image/jpeg",
                        "image/png",
                        "image/webp",
                    ),
                },
                system_owned_fields=frozenset({
                    "category",
                    "max_size_bytes",
                    "requires_virus_scan",
                    "generate_thumbnail",
                    "generate_preview",
                    "enable_ocr",
                    "optimise_image",
                    "extract_metadata",
                    "extensions",
                    "mime_types",
                }),
            ),
            ReferenceRecordDefinition(
                code="archive",
                values={
                    "name": "Archive File",
                    "description": (
                        "Policy for compressed archive uploads."
                    ),
                    "icon": "tabler:file-zip",
                    "colour": "#334155",
                    "sort_order": 90,
                    "is_active": True,
                    "category": FileCategory.ARCHIVE.value,
                    "max_size_bytes": 25 * 1024 * 1024,
                    "requires_virus_scan": True,
                    "generate_thumbnail": False,
                    "generate_preview": False,
                    "enable_ocr": False,
                    "optimise_image": False,
                    "extract_metadata": True,
                    "extensions": (
                        "zip",
                        "tar",
                        "gz",
                    ),
                    "mime_types": (
                        "application/zip",
                        "application/x-tar",
                        "application/gzip",
                    ),
                },
                system_owned_fields=frozenset({
                    "category",
                    "max_size_bytes",
                    "requires_virus_scan",
                    "generate_thumbnail",
                    "generate_preview",
                    "enable_ocr",
                    "optimise_image",
                    "extract_metadata",
                    "extensions",
                    "mime_types",
                }),
            ),
        ),
    )
)
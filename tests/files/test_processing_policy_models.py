from app.files.models import (
    FileCategory,
    FileProcessingExtensionRule,
    FileProcessingMimeTypeRule,
    FileProcessingPolicy,
)


def test_processing_policy_exposes_allowed_rules() -> None:
    policy = FileProcessingPolicy(
        code="pdf_document",
        name="PDF Document",
        category=FileCategory.DOCUMENT.value,
        max_size_bytes=10 * 1024 * 1024,
    )

    policy.extension_rules = [
        FileProcessingExtensionRule(
            extension="pdf",
        ),
    ]

    policy.mime_type_rules = [
        FileProcessingMimeTypeRule(
            mime_type="application/pdf",
        ),
    ]

    assert policy.category_value is FileCategory.DOCUMENT
    assert policy.allowed_extensions == {"pdf"}
    assert policy.allowed_mime_types == {
        "application/pdf"
    }


def test_processing_policy_is_custom_by_default() -> None:
    policy = FileProcessingPolicy(
        code="custom_document",
        name="Custom Document",
    )

    assert policy.is_custom is True


def test_processing_policy_display_name_uses_name() -> None:
    policy = FileProcessingPolicy(
        code="standard_image",
        name="Standard Image",
    )

    assert policy.display_name == "Standard Image"
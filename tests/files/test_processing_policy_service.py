import pytest

from app.extensions import db
from app.files.exceptions import (
    FileProcessingPolicyCodeConflictError,
    FileProcessingPolicyNameConflictError,
    InvalidFileProcessingPolicyError,
    ProtectedFileProcessingPolicyError,
)
from app.files.models import FileCategory
from app.files.processing_policies import (
    FileProcessingPolicyService,
)


@pytest.fixture
def policy_service(app):
    with app.app_context():
        yield FileProcessingPolicyService(
            session=db.session
        )

        db.session.rollback()


def test_create_processing_policy(
    app,
    policy_service,
) -> None:
    with app.app_context():
        policy = policy_service.create(
            code="test_pdf_document",
            name="PDF Document Test",
            category=FileCategory.DOCUMENT,
            max_size_bytes=10 * 1024 * 1024,
            extensions=["pdf", ".PDF"],
            mime_types=[
                "application/pdf",
                "application/pdf; charset=binary",
            ],
            generate_preview=True,
        )

        assert policy.code == "test_pdf_document"
        assert policy.category == "document"
        assert policy.allowed_extensions == {"pdf"}
        assert policy.allowed_mime_types == {
            "application/pdf"
        }
        assert policy.generate_preview is True


def test_create_rejects_duplicate_code(
    app,
    policy_service,
) -> None:
    with app.app_context():
        policy_service.create(
            code="test_duplicate_policy",
            name="Test First Policy",
            category=FileCategory.GENERIC,
            max_size_bytes=1024,
            extensions=["bin"],
            mime_types=[
                "application/octet-stream"
            ],
        )

        with pytest.raises(
            FileProcessingPolicyCodeConflictError
        ):
            policy_service.create(
                code="test_duplicate_policy",
                name="Test Second Policy",
                category=FileCategory.GENERIC,
                max_size_bytes=1024,
                extensions=["dat"],
                mime_types=[
                    "application/octet-stream"
                ],
            )


def test_create_rejects_duplicate_name_case_insensitive(
    app,
    policy_service,
) -> None:
    with app.app_context():
        policy_service.create(
            code="test_first_name",
            name="Standard Image Test",
            category=FileCategory.IMAGE,
            max_size_bytes=1024,
            extensions=["jpg"],
            mime_types=["image/jpeg"],
        )

        with pytest.raises(
            FileProcessingPolicyNameConflictError
        ):
            policy_service.create(
                code="test_second_name",
                name="standard image test",
                category=FileCategory.IMAGE,
                max_size_bytes=1024,
                extensions=["png"],
                mime_types=["image/png"],
            )


def test_create_rejects_invalid_category(
    app,
    policy_service,
) -> None:
    with app.app_context():
        with pytest.raises(
            InvalidFileProcessingPolicyError
        ):
            policy_service.create(
                code="test_invalid_category",
                name="Invalid Category Test",
                category="not_a_category",
                max_size_bytes=1024,
                extensions=["txt"],
                mime_types=["text/plain"],
            )


def test_update_replaces_rules(
    app,
    policy_service,
) -> None:
    with app.app_context():
        policy = policy_service.create(
            code="test_replace_rules",
            name="Replace Rules Test",
            category=FileCategory.IMAGE,
            max_size_bytes=1024,
            extensions=["jpg"],
            mime_types=["image/jpeg"],
        )

        updated = policy_service.update(
            policy.id,
            name="Replace Rules Updated",
            description="Updated policy.",
            category=FileCategory.IMAGE,
            max_size_bytes=2048,
            extensions=["png", "webp"],
            mime_types=[
                "image/png",
                "image/webp",
            ],
            icon="tabler:photo",
            colour="#0EA5A0",
            sort_order=20,
            requires_virus_scan=True,
            generate_thumbnail=True,
            generate_preview=True,
            enable_ocr=False,
            optimise_image=True,
            extract_metadata=True,
        )

        assert updated.code == "test_replace_rules"
        assert updated.name == (
            "Replace Rules Updated"
        )
        assert updated.allowed_extensions == {
            "png",
            "webp",
        }
        assert updated.allowed_mime_types == {
            "image/png",
            "image/webp",
        }
        assert updated.max_size_bytes == 2048


def test_deactivate_and_activate(
    app,
    policy_service,
) -> None:
    with app.app_context():
        policy = policy_service.create(
            code="test_lifecycle",
            name="Lifecycle Test",
            category=FileCategory.GENERIC,
            max_size_bytes=1024,
            extensions=["bin"],
            mime_types=[
                "application/octet-stream"
            ],
        )

        policy_service.deactivate(policy.id)
        assert policy.is_active is False

        policy_service.activate(policy.id)
        assert policy.is_active is True


def test_system_policy_cannot_be_deleted(
    app,
    policy_service,
) -> None:
    with app.app_context():
        policy = policy_service.create(
            code="test_protected_policy",
            name="Protected Policy Test",
            category=FileCategory.GENERIC,
            max_size_bytes=1024,
            extensions=["bin"],
            mime_types=[
                "application/octet-stream"
            ],
            is_system=True,
        )

        with pytest.raises(
            ProtectedFileProcessingPolicyError
        ):
            policy_service.delete_custom(
                policy.id
            )


def test_custom_policy_can_be_deleted(
    app,
    policy_service,
) -> None:
    with app.app_context():
        policy = policy_service.create(
            code="test_delete_policy",
            name="Delete Policy Test",
            category=FileCategory.GENERIC,
            max_size_bytes=1024,
            extensions=["bin"],
            mime_types=[
                "application/octet-stream"
            ],
        )

        policy_id = policy.id

        policy_service.delete_custom(policy_id)

        assert (
            db.session.get(
                type(policy),
                policy_id,
            )
            is None
        )
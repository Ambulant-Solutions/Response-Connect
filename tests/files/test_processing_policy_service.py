import pytest

from app.extensions import db
from app.files.commands import (
    CreateFileProcessingPolicyCommand,
    UpdateFileProcessingPolicyCommand,
)
from app.files.exceptions import (
    FileProcessingPolicyCodeConflictError,
    FileProcessingPolicyNameConflictError,
    InvalidFileProcessingPolicyError,
    ProtectedFileProcessingPolicyError,
)
from app.files.models import (
    FileCategory,
    FileProcessingPolicy,
)
from app.files.processing_policies import (
    FileProcessingPolicyService,
)
import logging

@pytest.fixture
def policy_service(app):
    """
    Provide a processing-policy service using the test application session.
    """

    with app.app_context():
        yield FileProcessingPolicyService(
            session=db.session,
        )

        db.session.rollback()


def test_create_processing_policy(
    app,
    policy_service,
) -> None:
    with app.app_context():
        policy = policy_service.create(
            CreateFileProcessingPolicyCommand(
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
        )

        assert policy.code == "test_pdf_document"
        assert policy.category == "document"
        assert policy.allowed_extensions == {"pdf"}
        assert policy.allowed_mime_types == {
            "application/pdf"
        }
        assert policy.generate_preview is True


def test_create_normalises_code(
    app,
    policy_service,
) -> None:
    with app.app_context():
        policy = policy_service.create(
            CreateFileProcessingPolicyCommand(
                code="  TEST_NORMALISED_CODE  ",
                name="Normalised Code Test",
                category=FileCategory.GENERIC,
                max_size_bytes=1024,
                extensions=["bin"],
                mime_types=[
                    "application/octet-stream"
                ],
            )
        )

        assert policy.code == "test_normalised_code"


def test_create_normalises_rules(
    app,
    policy_service,
) -> None:
    with app.app_context():
        policy = policy_service.create(
            CreateFileProcessingPolicyCommand(
                code="test_normalised_rules",
                name="Normalised Rules Test",
                category=FileCategory.IMAGE,
                max_size_bytes=1024,
                extensions=[
                    ".JPG",
                    "jpg",
                    " PNG ",
                ],
                mime_types=[
                    "IMAGE/JPEG",
                    "image/jpeg",
                    "image/png; charset=binary",
                ],
            )
        )

        assert policy.allowed_extensions == {
            "jpg",
            "png",
        }

        assert policy.allowed_mime_types == {
            "image/jpeg",
            "image/png",
        }


def test_create_rejects_duplicate_code(
    app,
    policy_service,
) -> None:
    with app.app_context():
        policy_service.create(
            CreateFileProcessingPolicyCommand(
                code="test_duplicate_policy",
                name="Test First Policy",
                category=FileCategory.GENERIC,
                max_size_bytes=1024,
                extensions=["bin"],
                mime_types=[
                    "application/octet-stream"
                ],
            )
        )

        with pytest.raises(
            FileProcessingPolicyCodeConflictError
        ):
            policy_service.create(
                CreateFileProcessingPolicyCommand(
                    code="test_duplicate_policy",
                    name="Test Second Policy",
                    category=FileCategory.GENERIC,
                    max_size_bytes=1024,
                    extensions=["dat"],
                    mime_types=[
                        "application/octet-stream"
                    ],
                )
            )


def test_create_rejects_duplicate_name_case_insensitive(
    app,
    policy_service,
) -> None:
    with app.app_context():
        policy_service.create(
            CreateFileProcessingPolicyCommand(
                code="test_first_name",
                name="Standard Image Test",
                category=FileCategory.IMAGE,
                max_size_bytes=1024,
                extensions=["jpg"],
                mime_types=["image/jpeg"],
            )
        )

        with pytest.raises(
            FileProcessingPolicyNameConflictError
        ):
            policy_service.create(
                CreateFileProcessingPolicyCommand(
                    code="test_second_name",
                    name="standard image test",
                    category=FileCategory.IMAGE,
                    max_size_bytes=1024,
                    extensions=["png"],
                    mime_types=["image/png"],
                )
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
                CreateFileProcessingPolicyCommand(
                    code="test_invalid_category",
                    name="Invalid Category Test",
                    category="not_a_category",
                    max_size_bytes=1024,
                    extensions=["txt"],
                    mime_types=["text/plain"],
                )
            )


def test_create_rejects_zero_maximum_size(
    app,
    policy_service,
) -> None:
    with app.app_context():
        with pytest.raises(
            InvalidFileProcessingPolicyError
        ):
            policy_service.create(
                CreateFileProcessingPolicyCommand(
                    code="test_zero_max_size",
                    name="Zero Maximum Size Test",
                    category=FileCategory.GENERIC,
                    max_size_bytes=0,
                    extensions=["bin"],
                    mime_types=[
                        "application/octet-stream"
                    ],
                )
            )


def test_create_rejects_empty_extensions(
    app,
    policy_service,
) -> None:
    with app.app_context():
        with pytest.raises(
            InvalidFileProcessingPolicyError
        ):
            policy_service.create(
                CreateFileProcessingPolicyCommand(
                    code="test_empty_extensions",
                    name="Empty Extensions Test",
                    category=FileCategory.GENERIC,
                    max_size_bytes=1024,
                    extensions=[],
                    mime_types=[
                        "application/octet-stream"
                    ],
                )
            )


def test_create_rejects_empty_mime_types(
    app,
    policy_service,
) -> None:
    with app.app_context():
        with pytest.raises(
            InvalidFileProcessingPolicyError
        ):
            policy_service.create(
                CreateFileProcessingPolicyCommand(
                    code="test_empty_mime_types",
                    name="Empty MIME Types Test",
                    category=FileCategory.GENERIC,
                    max_size_bytes=1024,
                    extensions=["bin"],
                    mime_types=[],
                )
            )


def test_create_rejects_invalid_extension(
    app,
    policy_service,
) -> None:
    with app.app_context():
        with pytest.raises(
            InvalidFileProcessingPolicyError
        ):
            policy_service.create(
                CreateFileProcessingPolicyCommand(
                    code="test_invalid_extension",
                    name="Invalid Extension Test",
                    category=FileCategory.GENERIC,
                    max_size_bytes=1024,
                    extensions=["not valid"],
                    mime_types=[
                        "application/octet-stream"
                    ],
                )
            )


def test_create_rejects_invalid_mime_type(
    app,
    policy_service,
) -> None:
    with app.app_context():
        with pytest.raises(
            InvalidFileProcessingPolicyError
        ):
            policy_service.create(
                CreateFileProcessingPolicyCommand(
                    code="test_invalid_mime_type",
                    name="Invalid MIME Type Test",
                    category=FileCategory.GENERIC,
                    max_size_bytes=1024,
                    extensions=["bin"],
                    mime_types=["not-a-mime-type"],
                )
            )


def test_update_replaces_rules(
    app,
    policy_service,
) -> None:
    with app.app_context():
        policy = policy_service.create(
            CreateFileProcessingPolicyCommand(
                code="test_replace_rules",
                name="Replace Rules Test",
                category=FileCategory.IMAGE,
                max_size_bytes=1024,
                extensions=["jpg"],
                mime_types=["image/jpeg"],
            )
        )

        updated = policy_service.update(
            policy.id,
            UpdateFileProcessingPolicyCommand(
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
            ),
        )

        assert updated.code == "test_replace_rules"
        assert updated.name == "Replace Rules Updated"
        assert updated.description == "Updated policy."
        assert updated.category == FileCategory.IMAGE.value
        assert updated.max_size_bytes == 2048

        assert updated.allowed_extensions == {
            "png",
            "webp",
        }

        assert updated.allowed_mime_types == {
            "image/png",
            "image/webp",
        }

        assert updated.icon == "tabler:photo"
        assert updated.colour == "#0EA5A0"
        assert updated.sort_order == 20
        assert updated.requires_virus_scan is True
        assert updated.generate_thumbnail is True
        assert updated.generate_preview is True
        assert updated.enable_ocr is False
        assert updated.optimise_image is True
        assert updated.extract_metadata is True


def test_update_preserves_stable_code(
    app,
    policy_service,
) -> None:
    with app.app_context():
        policy = policy_service.create(
            CreateFileProcessingPolicyCommand(
                code="test_stable_code",
                name="Stable Code Test",
                category=FileCategory.GENERIC,
                max_size_bytes=1024,
                extensions=["bin"],
                mime_types=[
                    "application/octet-stream"
                ],
            )
        )

        updated = policy_service.update(
            policy.id,
            UpdateFileProcessingPolicyCommand(
                name="Stable Code Updated",
                description=None,
                category=FileCategory.GENERIC,
                max_size_bytes=2048,
                extensions=["dat"],
                mime_types=[
                    "application/octet-stream"
                ],
                icon="tabler:file-settings",
                colour="#334155",
                sort_order=10,
                requires_virus_scan=True,
                generate_thumbnail=False,
                generate_preview=False,
                enable_ocr=False,
                optimise_image=False,
                extract_metadata=False,
            ),
        )

        assert updated.code == "test_stable_code"


def test_update_rejects_duplicate_name(
    app,
    policy_service,
) -> None:
    with app.app_context():
        first_policy = policy_service.create(
            CreateFileProcessingPolicyCommand(
                code="test_update_name_first",
                name="First Update Name",
                category=FileCategory.GENERIC,
                max_size_bytes=1024,
                extensions=["bin"],
                mime_types=[
                    "application/octet-stream"
                ],
            )
        )

        policy_service.create(
            CreateFileProcessingPolicyCommand(
                code="test_update_name_second",
                name="Second Update Name",
                category=FileCategory.GENERIC,
                max_size_bytes=1024,
                extensions=["dat"],
                mime_types=[
                    "application/octet-stream"
                ],
            )
        )

        with pytest.raises(
            FileProcessingPolicyNameConflictError
        ):
            policy_service.update(
                first_policy.id,
                UpdateFileProcessingPolicyCommand(
                    name="second update name",
                    description=None,
                    category=FileCategory.GENERIC,
                    max_size_bytes=1024,
                    extensions=["bin"],
                    mime_types=[
                        "application/octet-stream"
                    ],
                    icon="tabler:file-settings",
                    colour="#334155",
                    sort_order=0,
                    requires_virus_scan=True,
                    generate_thumbnail=False,
                    generate_preview=False,
                    enable_ocr=False,
                    optimise_image=False,
                    extract_metadata=False,
                ),
            )


def test_list_all_orders_by_sort_order_then_name(
    app,
    policy_service,
) -> None:
    with app.app_context():
        policy_service.create(
            CreateFileProcessingPolicyCommand(
                code="test_list_order_second",
                name="Beta Policy",
                category=FileCategory.GENERIC,
                max_size_bytes=1024,
                extensions=["bin"],
                mime_types=[
                    "application/octet-stream"
                ],
                sort_order=20,
            )
        )

        policy_service.create(
            CreateFileProcessingPolicyCommand(
                code="test_list_order_first",
                name="Alpha Policy",
                category=FileCategory.GENERIC,
                max_size_bytes=1024,
                extensions=["dat"],
                mime_types=[
                    "application/octet-stream"
                ],
                sort_order=10,
            )
        )

        policies = [
            policy
            for policy in policy_service.list_all()
            if policy.code.startswith(
                "test_list_order_"
            )
        ]

        assert [
            policy.code
            for policy in policies
        ] == [
            "test_list_order_first",
            "test_list_order_second",
        ]


def test_list_active_excludes_inactive_policy(
    app,
    policy_service,
) -> None:
    with app.app_context():
        active_policy = policy_service.create(
            CreateFileProcessingPolicyCommand(
                code="test_list_active",
                name="List Active Test",
                category=FileCategory.GENERIC,
                max_size_bytes=1024,
                extensions=["bin"],
                mime_types=[
                    "application/octet-stream"
                ],
            )
        )

        inactive_policy = policy_service.create(
            CreateFileProcessingPolicyCommand(
                code="test_list_inactive",
                name="List Inactive Test",
                category=FileCategory.GENERIC,
                max_size_bytes=1024,
                extensions=["dat"],
                mime_types=[
                    "application/octet-stream"
                ],
                is_active=False,
            )
        )

        active_ids = {
            policy.id
            for policy in policy_service.list_active()
        }

        assert active_policy.id in active_ids
        assert inactive_policy.id not in active_ids


def test_get_by_code_returns_policy_with_rules(
    app,
    policy_service,
) -> None:
    with app.app_context():
        created = policy_service.create(
            CreateFileProcessingPolicyCommand(
                code="test_get_by_code",
                name="Get By Code Test",
                category=FileCategory.DOCUMENT,
                max_size_bytes=1024,
                extensions=["pdf"],
                mime_types=["application/pdf"],
            )
        )

        policy = policy_service.get_by_code(
            "test_get_by_code"
        )

        assert policy.id == created.id
        assert policy.allowed_extensions == {"pdf"}
        assert policy.allowed_mime_types == {
            "application/pdf"
        }


def test_get_active_by_code_rejects_inactive_policy(
    app,
    policy_service,
) -> None:
    with app.app_context():
        policy_service.create(
            CreateFileProcessingPolicyCommand(
                code="test_get_inactive_by_code",
                name="Get Inactive By Code Test",
                category=FileCategory.GENERIC,
                max_size_bytes=1024,
                extensions=["bin"],
                mime_types=[
                    "application/octet-stream"
                ],
                is_active=False,
            )
        )

        from app.files.exceptions import (
            FileProcessingPolicyNotFoundError,
        )

        with pytest.raises(
            FileProcessingPolicyNotFoundError
        ):
            policy_service.get_active_by_code(
                "test_get_inactive_by_code"
            )


def test_deactivate_and_activate(
    app,
    policy_service,
) -> None:
    with app.app_context():
        policy = policy_service.create(
            CreateFileProcessingPolicyCommand(
                code="test_lifecycle",
                name="Lifecycle Test",
                category=FileCategory.GENERIC,
                max_size_bytes=1024,
                extensions=["bin"],
                mime_types=[
                    "application/octet-stream"
                ],
            )
        )

        deactivated = policy_service.deactivate(
            policy.id
        )

        assert deactivated.is_active is False

        activated = policy_service.activate(
            policy.id
        )

        assert activated.is_active is True


def test_deactivate_is_idempotent(
    app,
    policy_service,
) -> None:
    with app.app_context():
        policy = policy_service.create(
            CreateFileProcessingPolicyCommand(
                code="test_deactivate_idempotent",
                name="Deactivate Idempotent Test",
                category=FileCategory.GENERIC,
                max_size_bytes=1024,
                extensions=["bin"],
                mime_types=[
                    "application/octet-stream"
                ],
                is_active=False,
            )
        )

        result = policy_service.deactivate(
            policy.id
        )

        assert result.id == policy.id
        assert result.is_active is False


def test_activate_is_idempotent(
    app,
    policy_service,
) -> None:
    with app.app_context():
        policy = policy_service.create(
            CreateFileProcessingPolicyCommand(
                code="test_activate_idempotent",
                name="Activate Idempotent Test",
                category=FileCategory.GENERIC,
                max_size_bytes=1024,
                extensions=["bin"],
                mime_types=[
                    "application/octet-stream"
                ],
                is_active=True,
            )
        )

        result = policy_service.activate(
            policy.id
        )

        assert result.id == policy.id
        assert result.is_active is True


def test_system_policy_cannot_be_deleted(
    app,
    policy_service,
) -> None:
    with app.app_context():
        policy = policy_service.create(
            CreateFileProcessingPolicyCommand(
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
            CreateFileProcessingPolicyCommand(
                code="test_delete_policy",
                name="Delete Policy Test",
                category=FileCategory.GENERIC,
                max_size_bytes=1024,
                extensions=["bin"],
                mime_types=[
                    "application/octet-stream"
                ],
            )
        )

        policy_id = policy.id

        policy_service.delete_custom(
            policy_id
        )

        assert (
            db.session.get(
                FileProcessingPolicy,
                policy_id,
            )
            is None
        )

def test_create_emits_platform_log(
    app,
    policy_service,
    caplog,
) -> None:
    with app.app_context():
        with caplog.at_level(
            logging.INFO,
            logger=(
                "app.files.processing_policies"
            ),
        ):
            policy = policy_service.create(
                CreateFileProcessingPolicyCommand(
                    code="test_logged_create",
                    name="Logged Create Test",
                    category=FileCategory.GENERIC,
                    max_size_bytes=1024,
                    extensions=["bin"],
                    mime_types=[
                        "application/octet-stream"
                    ],
                )
            )

        matching_records = [
            record
            for record in caplog.records
            if getattr(
                record,
                "platform_event",
                None,
            )
            == "file_processing_policy.created"
        ]

        assert len(matching_records) == 1

        record = matching_records[0]

        assert record.policy_id == str(policy.id)
        assert record.policy_code == (
            "test_logged_create"
        )
        assert record.is_system is False

def test_deactivate_emits_log_only_on_change(
    app,
    policy_service,
    caplog,
) -> None:
    with app.app_context():
        policy = policy_service.create(
            CreateFileProcessingPolicyCommand(
                code="test_logged_deactivate",
                name="Logged Deactivate Test",
                category=FileCategory.GENERIC,
                max_size_bytes=1024,
                extensions=["bin"],
                mime_types=[
                    "application/octet-stream"
                ],
            )
        )

        caplog.clear()

        with caplog.at_level(
            logging.INFO,
            logger=(
                "app.files.processing_policies"
            ),
        ):
            policy_service.deactivate(policy.id)
            policy_service.deactivate(policy.id)

        matching_records = [
            record
            for record in caplog.records
            if getattr(
                record,
                "platform_event",
                None,
            )
            == (
                "file_processing_policy."
                "deactivated"
            )
        ]

        assert len(matching_records) == 1
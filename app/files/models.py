from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.catalogues import CatalogueMixin

class FileCategory(StrEnum):
    GENERIC = "generic"
    DOCUMENT = "document"
    IMAGE = "image"
    SPREADSHEET = "spreadsheet"
    PRESENTATION = "presentation"
    AUDIO = "audio"
    VIDEO = "video"
    ARCHIVE = "archive"

class FileProcessingPolicy(
    CatalogueMixin,
    db.Model,
):
    """
    A system-defined policy controlling technical file validation and
    processing behaviour.

    File types describe business meaning. Processing policies describe how
    uploaded bytes are validated and processed.
    """

    __tablename__ = "file_processing_policies"

    __table_args__ = (
        UniqueConstraint(
            "name",
            name="uq_file_processing_policies_name",
        ),
        CheckConstraint(
            "max_size_bytes > 0",
            name=(
                "ck_file_processing_policies_"
                "max_size_bytes_positive"
            ),
        ),
        CheckConstraint(
            "sort_order >= 0",
            name=(
                "ck_file_processing_policies_"
                "sort_order_non_negative"
            ),
        ),
        Index(
            "ix_file_processing_policies_active_order",
            "is_active",
            "sort_order",
            "name",
        ),
    )

    category: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=FileCategory.GENERIC.value,
        server_default=FileCategory.GENERIC.value,
    )

    max_size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=25 * 1024 * 1024,
        server_default=str(25 * 1024 * 1024),
    )

    requires_virus_scan: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
    )

    generate_thumbnail: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

    generate_preview: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

    enable_ocr: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

    optimise_image: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

    extract_metadata: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

    extension_rules: Mapped[
        list["FileProcessingExtensionRule"]
    ] = relationship(
        "FileProcessingExtensionRule",
        back_populates="processing_policy",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="FileProcessingExtensionRule.extension",
    )

    mime_type_rules: Mapped[
        list["FileProcessingMimeTypeRule"]
    ] = relationship(
        "FileProcessingMimeTypeRule",
        back_populates="processing_policy",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="FileProcessingMimeTypeRule.mime_type",
    )

    @property
    def category_value(self) -> FileCategory:
        return FileCategory(self.category)

    @property
    def allowed_extensions(self) -> set[str]:
        return {
            rule.extension
            for rule in self.extension_rules
        }

    @property
    def allowed_mime_types(self) -> set[str]:
        return {
            rule.mime_type
            for rule in self.mime_type_rules
        }

    def __repr__(self) -> str:
        return (
            f"<FileProcessingPolicy "
            f"code={self.code!r} "
            f"name={self.name!r}>"
        )

class FileProcessingExtensionRule(db.Model):
    """
    A normalised filename extension allowed by a processing policy.
    """

    __tablename__ = "file_processing_extension_rules"

    __table_args__ = (
        UniqueConstraint(
            "processing_policy_id",
            "extension",
            name=(
                "uq_file_processing_extension_rules_"
                "policy_extension"
            ),
        ),
        CheckConstraint(
            "extension = lower(extension)",
            name=(
                "ck_file_processing_extension_rules_"
                "extension_lowercase"
            ),
        ),
        CheckConstraint(
            "char_length(extension) > 0",
            name=(
                "ck_file_processing_extension_rules_"
                "extension_not_empty"
            ),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    processing_policy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "file_processing_policies.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    extension: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    processing_policy: Mapped[
        FileProcessingPolicy
    ] = relationship(
        "FileProcessingPolicy",
        back_populates="extension_rules",
    )

    def __repr__(self) -> str:
        return (
            f"<FileProcessingExtensionRule "
            f"extension={self.extension!r}>"
        )

class FileProcessingMimeTypeRule(db.Model):
    """
    A normalised MIME type allowed by a processing policy.
    """

    __tablename__ = "file_processing_mime_type_rules"

    __table_args__ = (
        UniqueConstraint(
            "processing_policy_id",
            "mime_type",
            name=(
                "uq_file_processing_mime_type_rules_"
                "policy_mime_type"
            ),
        ),
        CheckConstraint(
            "mime_type = lower(mime_type)",
            name=(
                "ck_file_processing_mime_type_rules_"
                "mime_type_lowercase"
            ),
        ),
        CheckConstraint(
            "position('/' in mime_type) > 1",
            name=(
                "ck_file_processing_mime_type_rules_"
                "mime_type_format"
            ),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    processing_policy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "file_processing_policies.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    mime_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    processing_policy: Mapped[
        FileProcessingPolicy
    ] = relationship(
        "FileProcessingPolicy",
        back_populates="mime_type_rules",
    )

    def __repr__(self) -> str:
        return (
            f"<FileProcessingMimeTypeRule "
            f"mime_type={self.mime_type!r}>"
        )


class FileObject(db.Model):
    """
    A file managed by Response Connect and stored in object storage.

    Feature-specific records, such as training evidence or incident
    attachments, should reference this record.
    """

    __tablename__ = "file_objects"

    __table_args__ = (
        UniqueConstraint(
            "bucket",
            "object_key",
            name="uq_file_objects_bucket_object_key",
        ),
        CheckConstraint(
            "size_bytes >= 0",
            name="ck_file_objects_size_bytes_non_negative",
        ),
        CheckConstraint(
            "char_length(sha256) = 64",
            name="ck_file_objects_sha256_length",
        ),
        Index(
            "ix_file_objects_created_at",
            "created_at",
        ),
        Index(
            "ix_file_objects_sha256",
            "sha256",
        ),
        Index(
            "ix_file_objects_active",
            "created_at",
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    uploaded_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "user_accounts.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    storage_backend: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="s3",
        server_default="s3",
    )

    bucket: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    object_key: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    mime_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="application/octet-stream",
        server_default="application/octet-stream",
    )

    extension: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )

    size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    sha256: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    uploaded_by: Mapped["UserAccount | None"] = relationship(
        "UserAccount",
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    @property
    def size_display(self) -> str:
        size = float(self.size_bytes)

        for unit in ("bytes", "KB", "MB", "GB", "TB"):
            if size < 1024 or unit == "TB":
                if unit == "bytes":
                    return f"{int(size)} {unit}"

                return f"{size:.1f} {unit}"

            size /= 1024

        return f"{self.size_bytes} bytes"

    def __repr__(self) -> str:
        return (
            f"<FileObject "
            f"id={self.id!s} "
            f"filename={self.original_filename!r}>"
        )


from app.blueprints.auth.models import UserAccount  # noqa: E402
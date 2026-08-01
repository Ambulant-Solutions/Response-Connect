from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
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
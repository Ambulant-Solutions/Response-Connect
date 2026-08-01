from __future__ import annotations

import uuid


class ObjectKeyGenerator:
    """Generate consistent object-storage keys."""

    @staticmethod
    def file_prefix(file_id: uuid.UUID) -> str:
        return f"files/{file_id}"

    @classmethod
    def original(cls, file_id: uuid.UUID) -> str:
        return f"{cls.file_prefix(file_id)}/original"

    @classmethod
    def thumbnail(
        cls,
        file_id: uuid.UUID,
        *,
        extension: str = "webp",
    ) -> str:
        safe_extension = cls._normalise_extension(extension)

        return (
            f"{cls.file_prefix(file_id)}/"
            f"thumbnail.{safe_extension}"
        )

    @classmethod
    def preview(
        cls,
        file_id: uuid.UUID,
        *,
        extension: str = "pdf",
    ) -> str:
        safe_extension = cls._normalise_extension(extension)

        return (
            f"{cls.file_prefix(file_id)}/"
            f"preview.{safe_extension}"
        )

    @staticmethod
    def _normalise_extension(extension: str) -> str:
        normalised = extension.strip().lower().lstrip(".")

        if not normalised:
            raise ValueError("A file extension is required.")

        if not normalised.replace("-", "").isalnum():
            raise ValueError(
                "The file extension contains invalid characters."
            )

        return normalised
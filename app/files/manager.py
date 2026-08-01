from __future__ import annotations

import hashlib
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from tempfile import SpooledTemporaryFile
from typing import BinaryIO, Any

from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.datastructures import FileStorage

from app.extensions import db
from app.files.exceptions import (
    DeletedFileError,
    FilePersistenceError,
    FileTooLargeError,
    InvalidFileError,
    ManagedFileNotFoundError,
    StorageError,
)
from app.files.keys import ObjectKeyGenerator
from app.files.models import FileObject
from app.files.providers import S3FileProvider


logger = logging.getLogger(__name__)

_COPY_CHUNK_SIZE = 1024 * 1024


class FileManager:
    """
    Coordinate database records and object-storage operations.

    The lower-level S3StorageService knows only about buckets and object keys.
    FileManager handles Response Connect's file records, hashes, filenames,
    deletion state and transactional compensation.
    """

    def __init__(
        self,
        provider: S3FileProvider,
        *,
        max_upload_bytes: int,
        spool_max_bytes: int,
    ) -> None:
        if max_upload_bytes <= 0:
            raise ValueError(
                "max_upload_bytes must be greater than zero."
            )

        if spool_max_bytes <= 0:
            raise ValueError(
                "spool_max_bytes must be greater than zero."
            )

        self.provider = provider
        self.max_upload_bytes = max_upload_bytes
        self.spool_max_bytes = spool_max_bytes

    @classmethod
    def from_app_config(
        cls,
        provider: S3FileProvider,
    ) -> "FileManager":
        return cls(
            storage,
            max_upload_bytes=current_app.config[
                "FILE_UPLOAD_MAX_BYTES"
            ],
            spool_max_bytes=current_app.config[
                "FILE_UPLOAD_SPOOL_MAX_BYTES"
            ],
        )

    def create_file(
        self,
        source: BinaryIO,
        *,
        original_filename: str,
        content_type: str | None = None,
        uploaded_by_id: uuid.UUID | None = None,
    ) -> FileObject:
        """
        Copy, validate, hash and upload a file, then persist its metadata.

        This method commits the new FileObject record. If the database commit
        fails after the S3 upload, it attempts to remove the uploaded object.
        """

        cleaned_filename = self._clean_filename(
            original_filename
        )

        normalised_content_type = self._normalise_content_type(
            content_type
        )

        file_id = uuid.uuid4()
        object_key = ObjectKeyGenerator.original(file_id)

        temporary_file, size_bytes, sha256 = (
            self._prepare_source(source)
        )

        extension = self._extract_extension(
            cleaned_filename
        )

        uploaded = False

        try:
            temporary_file.seek(0)

            self.provider.upload_fileobj(
                temporary_file,
                object_key,
                content_type=normalised_content_type,
                metadata={
                    "file-id": str(file_id),
                    "sha256": sha256,
                },
            )

            uploaded = True

            file_object = FileObject(
                id=file_id,
                uploaded_by_id=uploaded_by_id,
                storage_backend="s3",
                bucket=self.provider.bucket,
                object_key=object_key,
                original_filename=cleaned_filename,
                mime_type=normalised_content_type,
                extension=extension,
                size_bytes=size_bytes,
                sha256=sha256,
            )

            db.session.add(file_object)
            db.session.commit()

            return file_object

        except SQLAlchemyError as exc:
            db.session.rollback()

            cleanup_error = self._cleanup_failed_upload(
                object_key
            ) if uploaded else None

            if cleanup_error is not None:
                raise FilePersistenceError(
                    "The file metadata could not be saved and the "
                    f"uploaded object could not be removed. "
                    f"Orphaned object key: {object_key!r}."
                ) from exc

            raise FilePersistenceError(
                "The file was uploaded but its database record "
                "could not be saved. The uploaded object was removed."
            ) from exc

        finally:
            temporary_file.close()

    def create_from_filestorage(
        self,
        upload: FileStorage,
        *,
        uploaded_by_id: uuid.UUID | None = None,
    ) -> FileObject:
        """
        Create a managed file from a Flask/Werkzeug FileStorage object.
        """

        if upload is None:
            raise InvalidFileError(
                "No uploaded file was provided."
            )

        if not upload.filename:
            raise InvalidFileError(
                "The uploaded file has no filename."
            )

        return self.create_file(
            upload.stream,
            original_filename=upload.filename,
            content_type=upload.mimetype,
            uploaded_by_id=uploaded_by_id,
        )

    def get_file(
        self,
        file_id: uuid.UUID,
        *,
        include_deleted: bool = False,
    ) -> FileObject:
        file_object = db.session.get(
            FileObject,
            file_id,
        )

        if file_object is None:
            raise ManagedFileNotFoundError(
                f"File {file_id} does not exist."
            )

        if file_object.is_deleted and not include_deleted:
            raise ManagedFileNotFoundError(
                f"File {file_id} does not exist."
            )

        return file_object

    def open_download(
        self,
        file_object: FileObject,
    ) -> tuple[Any, int | None, str]:
        """
        Open a stored object for streaming through Flask.

        Returns:
            body: botocore StreamingBody
            content_length: object size where available
            content_type: response MIME type
        """

        if file_object.is_deleted:
            raise DeletedFileError(
                "Deleted files cannot be downloaded."
            )

        response = self.provider.get_object(
            file_object.object_key
        )

        body = response["Body"]

        content_length = response.get(
            "ContentLength",
            file_object.size_bytes,
        )

        content_type = response.get(
            "ContentType",
            file_object.mime_type,
        )

        return (
            body,
            content_length,
            content_type,
        )

    def download_fileobj(
        self,
        file_object: FileObject,
        destination: BinaryIO,
    ) -> None:
        if file_object.is_deleted:
            raise DeletedFileError(
                "Deleted files cannot be downloaded."
            )

        self.provider.download_fileobj(
            file_object.object_key,
            destination,
        )

    def soft_delete(
        self,
        file_object: FileObject,
    ) -> FileObject:
        """
        Mark a file as deleted without removing its stored object.

        Keeping the object allows retention policies, audit review and
        accidental-deletion recovery to be implemented later.
        """

        if file_object.is_deleted:
            return file_object

        file_object.deleted_at = datetime.now(timezone.utc)

        try:
            db.session.commit()
        except SQLAlchemyError as exc:
            db.session.rollback()

            raise FilePersistenceError(
                "The file could not be marked as deleted."
            ) from exc

        return file_object

    def restore(
        self,
        file_object: FileObject,
    ) -> FileObject:
        if not file_object.is_deleted:
            return file_object

        if not self.provider.object_exists(
            file_object.object_key
        ):
            raise FilePersistenceError(
                "The file record cannot be restored because "
                "its stored object no longer exists."
            )

        file_object.deleted_at = None

        try:
            db.session.commit()
        except SQLAlchemyError as exc:
            db.session.rollback()

            raise FilePersistenceError(
                "The file could not be restored."
            ) from exc

        return file_object

    def purge(
        self,
        file_object: FileObject,
    ) -> None:
        """
        Permanently remove a soft-deleted file.

        Purge is intentionally separate from soft deletion. Feature routes
        should not normally expose this directly to ordinary users.
        """

        if not file_object.is_deleted:
            raise FileManagementError(
                "A file must be soft deleted before it can be purged."
            )

        try:
            self.provider.delete_object(
                file_object.object_key
            )
        except StorageError:
            raise

        try:
            db.session.delete(file_object)
            db.session.commit()

        except SQLAlchemyError as exc:
            db.session.rollback()

            raise FilePersistenceError(
                "The stored object was removed, but the database "
                "record could not be deleted. Manual reconciliation "
                f"may be required for file {file_object.id}."
            ) from exc

    def _prepare_source(
        self,
        source: BinaryIO,
    ) -> tuple[BinaryIO, int, str]:
        if source is None:
            raise InvalidFileError(
                "No file source was provided."
            )

        temporary_file = SpooledTemporaryFile(
            max_size=self.spool_max_bytes,
            mode="w+b",
        )

        digest = hashlib.sha256()
        size_bytes = 0

        try:
            while True:
                chunk = source.read(_COPY_CHUNK_SIZE)

                if not chunk:
                    break

                if not isinstance(
                    chunk,
                    (bytes, bytearray),
                ):
                    raise InvalidFileError(
                        "The uploaded source must provide binary data."
                    )

                size_bytes += len(chunk)

                if size_bytes > self.max_upload_bytes:
                    raise FileTooLargeError(
                        "The uploaded file exceeds the maximum "
                        f"size of {self.max_upload_bytes} bytes."
                    )

                digest.update(chunk)
                temporary_file.write(chunk)

            if size_bytes == 0:
                raise InvalidFileError(
                    "Empty files cannot be uploaded."
                )

            temporary_file.seek(0)

            return (
                temporary_file,
                size_bytes,
                digest.hexdigest(),
            )

        except Exception:
            temporary_file.close()
            raise

    @staticmethod
    def _clean_filename(
        filename: str,
    ) -> str:
        if not filename:
            raise InvalidFileError(
                "A filename is required."
            )

        # Treat both slash styles as path separators, then retain only
        # the final component.
        cleaned = filename.replace("\\", "/").split("/")[-1]

        cleaned = "".join(
            character
            for character in cleaned
            if character.isprintable()
            and character not in {"\r", "\n", "\x00"}
        ).strip()

        if cleaned in {"", ".", ".."}:
            raise InvalidFileError(
                "The filename is invalid."
            )

        if len(cleaned) > 255:
            suffix = Path(cleaned).suffix
            stem_limit = max(
                1,
                255 - len(suffix),
            )

            cleaned = (
                f"{Path(cleaned).stem[:stem_limit]}"
                f"{suffix}"
            )

        return cleaned

    @staticmethod
    def _normalise_content_type(
        content_type: str | None,
    ) -> str:
        if not content_type:
            return "application/octet-stream"

        cleaned = (
            content_type
            .split(";", 1)[0]
            .strip()
            .lower()
        )

        if not cleaned or "/" not in cleaned:
            return "application/octet-stream"

        return cleaned[:255]

    @staticmethod
    def _extract_extension(
        filename: str,
    ) -> str | None:
        suffix = Path(filename).suffix.lower().lstrip(".")

        if not suffix:
            return None

        cleaned = "".join(
            character
            for character in suffix
            if character.isalnum()
        )

        return cleaned[:32] or None

    def _cleanup_failed_upload(
        self,
        object_key: str,
    ) -> Exception | None:
        try:
            self.provider.delete_object(object_key)
            return None

        except Exception as exc:
            logger.exception(
                "Unable to remove object after database failure: %s",
                object_key,
            )
            return exc
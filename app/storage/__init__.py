from flask import g

from app.storage.manager import FileManager
from app.storage.models import FileObject
from app.storage.service import S3StorageService
from app.storage.http import (
    build_content_disposition,
    iter_s3_body,
)


def get_storage_service() -> S3StorageService:
    """
    Return one configured storage-service instance per Flask context.
    """

    if "storage_service" not in g:
        g.storage_service = (
            S3StorageService.from_app_config()
        )

    return g.storage_service


def get_file_manager() -> FileManager:
    """
    Return one configured file-manager instance per Flask context.
    """

    if "file_manager" not in g:
        g.file_manager = FileManager.from_app_config(
            get_storage_service()
        )

    return g.file_manager


__all__ = [
    "FileManager",
    "FileObject",
    "S3StorageService",
    "get_file_manager",
    "get_storage_service",
]
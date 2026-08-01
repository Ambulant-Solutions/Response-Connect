from flask import g

from app.files.manager import FileManager
from app.files.models import FileObject
from app.files.providers import S3FileProvider
from app.files.http import (
    build_content_disposition,
    iter_s3_body,
)


def get_file_provider() -> S3FileProvider:
    if "file_provider" not in g:
        g.file_provider = S3FileProvider.from_app_config()

    return g.file_provider


def get_file_manager() -> FileManager:
    if "file_manager" not in g:
        g.file_manager = FileManager.from_app_config(
            get_file_provider()
        )

    return g.file_manager


__all__ = [
    "FileManager",
    "FileObject",
    "S3FileProvider",
    "get_file_manager",
    "get_file_provider",
]
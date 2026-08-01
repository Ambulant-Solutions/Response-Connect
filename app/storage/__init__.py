from app.storage.models import FileObject
from app.storage.service import S3StorageService


def get_storage_service() -> S3StorageService:
    """
    Return a storage service configured from the current Flask application.
    """

    return S3StorageService.from_app_config()


__all__ = [
    "FileObject",
    "S3StorageService",
    "get_storage_service",
]
from flask import g

from app.files.manager import FileManager
from app.files.models import FileObject
from app.files.providers import S3FileProvider
from app.files.http import (
    build_content_disposition,
    iter_s3_body,
)
from app.extensions import db
from app.files.processing_policies import (
    FileProcessingPolicyService,
)
from app.files.processing_policies import (
    FileProcessingPolicyService,
    FileProcessingPolicySynchroniser,
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

def get_file_processing_policy_service(
) -> FileProcessingPolicyService:
    """
    Return one processing-policy service per Flask context.
    """

    if "file_processing_policy_service" not in g:
        g.file_processing_policy_service = (
            FileProcessingPolicyService(
                session=db.session,
            )
        )

    return g.file_processing_policy_service

def get_file_processing_policy_synchroniser(
) -> FileProcessingPolicySynchroniser:
    if (
        "file_processing_policy_synchroniser"
        not in g
    ):
        g.file_processing_policy_synchroniser = (
            FileProcessingPolicySynchroniser(
                service=(
                    get_file_processing_policy_service()
                )
            )
        )

    return g.file_processing_policy_synchroniser


__all__ = [
    "FileManager",
    "FileObject",
    "FileProcessingPolicyService",
    "S3FileProvider",
    "get_file_manager",
    "get_file_processing_policy_service",
    "get_file_provider",
    "FileProcessingPolicySynchroniser",
    "get_file_processing_policy_synchroniser",
]
from __future__ import annotations

from typing import BinaryIO, Any

import boto3
from botocore.client import BaseClient
from botocore.config import Config as BotoConfig
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
    EndpointConnectionError,
)
from flask import current_app

from app.files.exceptions import (
    StorageConfigurationError,
    StorageConnectionError,
    StorageError,
    StorageObjectNotFoundError,
)


class S3FileProvider:
    """
    Provider-neutral storage service for S3-compatible object storage.

    Application routes and business services should use this class rather than
    importing boto3 directly.
    """

    def __init__(
        self,
        *,
        endpoint_url: str,
        region: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        use_ssl: bool = False,
        addressing_style: str = "path",
        presigned_url_expiry: int = 300,
    ) -> None:
        if not endpoint_url:
            raise StorageConfigurationError(
                "S3_ENDPOINT_URL is not configured."
            )

        if not access_key:
            raise StorageConfigurationError(
                "S3_ACCESS_KEY is not configured."
            )

        if not secret_key:
            raise StorageConfigurationError(
                "S3_SECRET_KEY is not configured."
            )

        if not bucket:
            raise StorageConfigurationError(
                "S3_BUCKET is not configured."
            )

        if addressing_style not in {"path", "virtual", "auto"}:
            raise StorageConfigurationError(
                "S3_ADDRESSING_STYLE must be path, virtual or auto."
            )

        self.endpoint_url = endpoint_url
        self.region = region
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = bucket
        self.use_ssl = use_ssl
        self.addressing_style = addressing_style
        self.presigned_url_expiry = presigned_url_expiry

        self._client: BaseClient | None = None

    @classmethod
    def from_app_config(cls) -> "S3StorageService":
        return cls(
            endpoint_url=current_app.config["S3_ENDPOINT_URL"],
            region=current_app.config["S3_REGION"],
            access_key=current_app.config["S3_ACCESS_KEY"],
            secret_key=current_app.config["S3_SECRET_KEY"],
            bucket=current_app.config["S3_BUCKET"],
            use_ssl=current_app.config["S3_USE_SSL"],
            addressing_style=current_app.config[
                "S3_ADDRESSING_STYLE"
            ],
            presigned_url_expiry=current_app.config[
                "S3_PRESIGNED_URL_EXPIRY"
            ],
        )

    @property
    def client(self) -> BaseClient:
        if self._client is None:
            self._client = boto3.client(
                "s3",
                endpoint_url=self.endpoint_url,
                region_name=self.region,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                use_ssl=self.use_ssl,
                config=BotoConfig(
                    signature_version="s3v4",
                    s3={
                        "addressing_style": self.addressing_style,
                    },
                ),
            )

        return self._client

    def initialise_bucket(self) -> None:
        """
        Verify access to object storage and create the configured bucket when
        it does not already exist.
        """

        try:
            self.client.head_bucket(Bucket=self.bucket)
            return

        except EndpointConnectionError as exc:
            raise StorageConnectionError(
                f"Unable to connect to object storage at "
                f"{self.endpoint_url}."
            ) from exc

        except ClientError as exc:
            error_code = str(
                exc.response.get("Error", {}).get("Code", "")
            )

            if error_code not in {
                "404",
                "NoSuchBucket",
                "NotFound",
            }:
                raise StorageConnectionError(
                    f"Unable to access S3 bucket "
                    f"{self.bucket!r}: {error_code or 'unknown error'}."
                ) from exc

        try:
            create_arguments = {
                "Bucket": self.bucket,
            }

            # AWS requires a location constraint outside us-east-1.
            # MinIO accepts bucket creation without it.
            if (
                "amazonaws.com" in self.endpoint_url
                and self.region != "us-east-1"
            ):
                create_arguments["CreateBucketConfiguration"] = {
                    "LocationConstraint": self.region,
                }

            self.client.create_bucket(**create_arguments)

        except EndpointConnectionError as exc:
            raise StorageConnectionError(
                f"Unable to connect to object storage at "
                f"{self.endpoint_url}."
            ) from exc

        except (BotoCoreError, ClientError) as exc:
            raise StorageError(
                f"Unable to create S3 bucket {self.bucket!r}."
            ) from exc

    def object_exists(self, object_key: str) -> bool:
        try:
            self.client.head_object(
                Bucket=self.bucket,
                Key=object_key,
            )
            return True

        except ClientError as exc:
            error_code = str(
                exc.response.get("Error", {}).get("Code", "")
            )

            if error_code in {
                "404",
                "NoSuchKey",
                "NotFound",
            }:
                return False

            raise StorageError(
                f"Unable to check object {object_key!r}."
            ) from exc

        except BotoCoreError as exc:
            raise StorageError(
                f"Unable to check object {object_key!r}."
            ) from exc

    def get_object(
        self,
        object_key: str,
    ) -> dict[str, Any]:
        """
        Return an S3 object response containing a streaming body.

        The caller is responsible for closing the returned Body.
        """

        try:
            return self.client.get_object(
                Bucket=self.bucket,
                Key=object_key,
            )

        except ClientError as exc:
            error_code = str(
                exc.response.get("Error", {}).get("Code", "")
            )

            if error_code in {
                "404",
                "NoSuchKey",
                "NotFound",
            }:
                raise StorageObjectNotFoundError(
                    f"Object {object_key!r} does not exist."
                ) from exc

            raise StorageError(
                f"Unable to open object {object_key!r}."
            ) from exc

        except BotoCoreError as exc:
            raise StorageError(
                f"Unable to open object {object_key!r}."
            ) from exc

    def upload_fileobj(
        self,
        file_object: BinaryIO,
        object_key: str,
        *,
        content_type: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> None:
        extra_args: dict[str, object] = {}

        if content_type:
            extra_args["ContentType"] = content_type

        if metadata:
            extra_args["Metadata"] = metadata

        try:
            self.client.upload_fileobj(
                Fileobj=file_object,
                Bucket=self.bucket,
                Key=object_key,
                ExtraArgs=extra_args or None,
            )

        except (BotoCoreError, ClientError) as exc:
            raise StorageError(
                f"Unable to upload object {object_key!r}."
            ) from exc

    def download_fileobj(
        self,
        object_key: str,
        file_object: BinaryIO,
    ) -> None:
        try:
            self.client.download_fileobj(
                Bucket=self.bucket,
                Key=object_key,
                Fileobj=file_object,
            )

        except ClientError as exc:
            error_code = str(
                exc.response.get("Error", {}).get("Code", "")
            )

            if error_code in {
                "404",
                "NoSuchKey",
                "NotFound",
            }:
                raise StorageObjectNotFoundError(
                    f"Object {object_key!r} does not exist."
                ) from exc

            raise StorageError(
                f"Unable to download object {object_key!r}."
            ) from exc

        except BotoCoreError as exc:
            raise StorageError(
                f"Unable to download object {object_key!r}."
            ) from exc

    def delete_object(self, object_key: str) -> None:
        try:
            self.client.delete_object(
                Bucket=self.bucket,
                Key=object_key,
            )

        except (BotoCoreError, ClientError) as exc:
            raise StorageError(
                f"Unable to delete object {object_key!r}."
            ) from exc

    def create_presigned_download_url(
        self,
        object_key: str,
        *,
        expiry: int | None = None,
        download_filename: str | None = None,
    ) -> str:
        parameters: dict[str, str] = {
            "Bucket": self.bucket,
            "Key": object_key,
        }

        if download_filename:
            safe_filename = (
                download_filename
                .replace("\\", "_")
                .replace('"', "")
                .replace("\r", "")
                .replace("\n", "")
            )

            parameters["ResponseContentDisposition"] = (
                f'attachment; filename="{safe_filename}"'
            )

        try:
            return self.client.generate_presigned_url(
                ClientMethod="get_object",
                Params=parameters,
                ExpiresIn=expiry or self.presigned_url_expiry,
            )

        except (BotoCoreError, ClientError) as exc:
            raise StorageError(
                f"Unable to create download URL for "
                f"{object_key!r}."
            ) from exc
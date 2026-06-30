"""S3-compatible storage backend (MinIO locally, AWS S3 in prod).

The only module that imports boto3.
"""
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from app.config import settings
from app.core.errors import not_found
from app.core.logging_config import get_logger
from app.storage.base import StorageBackend, StoredObject

_log = get_logger("app.storage.s3")


class S3Backend(StorageBackend):
    def __init__(self) -> None:
        self._bucket = settings.s3_bucket
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region,
            config=Config(signature_version="s3v4"),
        )
        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        try:
            self._client.head_bucket(Bucket=self._bucket)
        except ClientError:
            self._client.create_bucket(Bucket=self._bucket)
            _log.info("created_bucket", extra={"bucket": self._bucket})

    def put(self, key: str, data: bytes, content_type: str, filename: str) -> str:
        self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
            Metadata={"filename": filename},
        )
        _log.info("stored_object", extra={"key": key, "bytes": len(data)})
        return key

    def get(self, key: str) -> StoredObject:
        try:
            obj = self._client.get_object(Bucket=self._bucket, Key=key)
        except ClientError as exc:
            raise not_found("RESUME_NOT_FOUND", "Resume file not found") from exc
        meta = obj.get("Metadata", {})
        return StoredObject(
            data=obj["Body"].read(),
            content_type=obj.get("ContentType", "application/octet-stream"),
            filename=meta.get("filename", key.rsplit("/", 1)[-1]),
        )

    def delete(self, key: str) -> None:
        self._client.delete_object(Bucket=self._bucket, Key=key)

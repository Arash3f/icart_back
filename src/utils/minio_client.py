from datetime import timedelta

from minio import Minio
from minio.versioningconfig import ENABLED, VersioningConfig
from pydantic import BaseModel


# Todo: documentation
# ---------------------------------------------------------------
class IMinioResponse(BaseModel):
    bucket_name: str
    file_name: str


# ---------------------------------------------------------------
class MinioClient:
    def __init__(
        self,
        url: str,
        access_key: str,
        secret_key: str,
        default_bucket: str,
        site_media_bucket: str,
        profile_image_bucket: str,
        capital_transfer_media_bucket: str,
        contract_media: str,
    ):
        self.minio_url = url
        self.access_key = access_key
        self.secret_key = secret_key
        self.client = Minio(
            endpoint=self.minio_url,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False,
        )
        self.make_bucket(
            [
                default_bucket,
                site_media_bucket,
                profile_image_bucket,
                capital_transfer_media_bucket,
                contract_media,
            ],
        )

    def make_bucket(self, buckets: list[str]) -> bool:
        for bucket in buckets:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)
                self.client.set_bucket_versioning(bucket, VersioningConfig(ENABLED))
        return True

    def presigned_get_object(self, bucket_name, object_name):
        url = self.client.get_presigned_url(
            bucket_name=bucket_name,
            object_name=object_name,
            expires=timedelta(days=7),
        )
        return url

    def check_file_name_exists(self, bucket_name, file_name):
        try:
            self.client.stat_object(bucket_name=bucket_name, object_name=file_name)
            return True
        except Exception as e:
            print(f"[x] Exception {e}")
            return False

    def put_object(self, file_data, file_name, content_type):
        try:
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=file_name,
                data=file_data,
                content_type=content_type,
                length=-1,
                part_size=10 * 1024 * 1024,
            )
            data_file = IMinioResponse(
                bucket_name=self.bucket_name,
                file_name=file_name,
            )
            return data_file
        except Exception as e:
            raise e

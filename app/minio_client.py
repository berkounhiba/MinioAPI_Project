from minio import Minio
from io import BytesIO

MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
BUCKET_NAME = "files"

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

# Create bucket if not exists
if not minio_client.bucket_exists(BUCKET_NAME):
    minio_client.make_bucket(BUCKET_NAME)

print("MINIO_ENDPOINT =", MINIO_ENDPOINT)


def upload_file(file_data: BytesIO, object_name: str, content_type: str):
    minio_client.put_object(
        BUCKET_NAME,
        object_name,
        file_data,
        length=-1,
        part_size=10 * 1024 * 1024,
        content_type=content_type
    )


def download_file(object_name: str):
    return minio_client.get_object(BUCKET_NAME, object_name)


def delete_file(object_name: str):
    minio_client.remove_object(BUCKET_NAME, object_name)

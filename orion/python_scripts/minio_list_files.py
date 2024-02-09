# https://min.io/docs/minio/linux/developers/python/minio-py.html

# file_uploader.py MinIO Python SDK example
from minio import Minio
from minio.error import S3Error

def main():
    # Create a MinIO client
    client = Minio("cabbage-xps-8900:9000",
        access_key="KODXtyXxsNTbFrLEitSg",
        secret_key="Ym3Cg3PHbjyIL35V6PEtp3ZQiNeIHeIYUgVC4cq0",
        secure=False
    )

    # The bucket name on the MinIO server
    #bucket_name = "test"

    # List objects
    objects = client.list_objects('test', recursive=True)
    for obj in objects:
        print(obj.object_name)

if __name__ == "__main__":
    try:
        main()
    except S3Error as exc:
        print("error occurred.", exc)
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

    # The file to upload, change this path if needed
    source_file = "photo001.jpg"

    # The destination bucket and filename on the MinIO server
    bucket_name = "vineyard001"
    destination_file = "block001/vinerow001/vine002/photo001.jpg"

    # Make the bucket if it doesn't exist.
    found = client.bucket_exists(bucket_name)
    if not found:
        client.make_bucket(bucket_name)
        print("Created bucket", bucket_name)
    else:
        print("Bucket", bucket_name, "already exists")

    # Upload the file, renaming it in the process
    client.fput_object(
        bucket_name, destination_file, source_file,
    )
    print(
        source_file, "successfully uploaded as object",
        destination_file, "to bucket", bucket_name,
    )

if __name__ == "__main__":
    try:
        main()
    except S3Error as exc:
        print("error occurred.", exc)
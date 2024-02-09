from minio import Minio
from minio.error import S3Error

# Constants
MINIO_SERVER = "cabbage-xps-8900:9000"
MINIO_ACCESS_KEY = "KODXtyXxsNTbFrLEitSg"
MINIO_SECRET_KEY = "Ym3Cg3PHbjyIL35V6PEtp3ZQiNeIHeIYUgVC4cq0"
MINIO_SECURE = False

def initialize_minio_client():
    return Minio(MINIO_SERVER, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=MINIO_SECURE)

def download_file_from_minio(client, bucket_name, source_file, destination_path):
    try:
        client.fget_object(bucket_name, source_file, destination_path)
        print(f"Downloaded {source_file} from bucket {bucket_name} to {destination_path} successfully")
    except S3Error as exc:
        print(f"Failed to download {source_file}. Error: {exc}")

def main():
    try:
        minio_client = initialize_minio_client()

        # Specify the bucket name, file name, and the local destination path
        bucket_name = "vineyard1"
        source_file = "FRGRA32772.jpg"
        destination_path = "downloaded_file.jpg"

        download_file_from_minio(minio_client, bucket_name, source_file, destination_path)

    except S3Error as exc:
        print("Error occurred:", exc)

if __name__ == "__main__":
    main()

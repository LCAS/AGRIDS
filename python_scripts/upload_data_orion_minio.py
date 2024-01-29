from minio import Minio
from minio.error import S3Error

import requests
import json

MINIO_SERVER = "cabbage-xps-8900:9000"
MINIO_ACCESS_KEY = "KODXtyXxsNTbFrLEitSg"
MINIO_SECRET_KEY = "Ym3Cg3PHbjyIL35V6PEtp3ZQiNeIHeIYUgVC4cq0"
MINIO_SECURE = False

# folder and file names for objects (photos)  stored in minio storage
# folder structure vineyard_name/block_name/vine_row_name/vine_name/file_name.jpg
# to upload to minio bucket name = vineyard_name and object name = block_name/vine_row_name/vine_name/file_name.jpg
vineyard_name = "vineyard001"
block_name = "block001"
vine_row_name = "vinerow001"
vine_name = "vine003"
file_name = "photo003.jpg"
destination_file_name = destination_file_name = block_name + "/" + vine_row_name + "/" +vine_name + "/" + file_name

FIWARE_ORION_URL = "http://cabbage-xps-8900:1026/v2/entities"

def initialize_minio_client():
    return Minio(MINIO_SERVER, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=MINIO_SECURE)

def create_or_get_bucket(client, bucket_name):
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        print("Created bucket", bucket_name)
    else:
        print("Bucket", bucket_name, "already exists")

def upload_file_to_minio(client, bucket_name, destination_file, source_file):
    client.fput_object(bucket_name, destination_file, source_file)
    print(f"{source_file} successfully uploaded as object {destination_file} to bucket {bucket_name}")

def add_data_to_fiware_orion(bucket_name, destination_file):
    url = FIWARE_ORION_URL
    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "id": "vine003",
        "type": "Vine",
        "vinerow_id": {
            "value": "vinerow001",
            "type": "String"
        },
        "block_id": {
            "value": "block001",
            "type": "String"
        },
        "vineyard_id": {
            "value": "vineyard001",
            "type": "String"
        },
        "user_defined_id": {
            "value": "Vine 3",
            "type": "String"
        },
        "variety": {
            "value": "Pinot Noir",
            "type": "String"
        },
        "clone": {
            "value": "Pinot Meunier",
            "type": "String"
        },
        "rootstock": {
            "value": "1570C",
            "type": "String"
        },
        "location": {
            "type": "geo:json",
            "value": {
                "type": "Point",
                "coordinates": [53.227292304487605, -0.5486788194799487]
            }
        },
        "photo": {
            "type": "URL",
            "value": f"{vineyard_name}/{block_name}/{vine_row_name}/{vine_name}/{file_name}"
        }
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        print("Entity created successfully")
    else:
        print("Failed to create entity. Status code:", response.status_code)
        print("Response:", response.text)

def main():
    try:
        minio_client = initialize_minio_client()

        create_or_get_bucket(minio_client, vineyard_name)

        upload_file_to_minio(minio_client, vineyard_name, destination_file_name, file_name)

        add_data_to_fiware_orion(vineyard_name, file_name)

    except S3Error as exc:
        print("Error occurred:", exc)

if __name__ == "__main__":
    main()

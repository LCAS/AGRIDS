import zenoh
import time
from minio import Minio
from io import BytesIO

import orion_add_image

# Connect to MinIO
minio_client = Minio(
    "cabbage-xps-8900:9000",
    access_key="KODXtyXxsNTbFrLEitSg",
    secret_key="Ym3Cg3PHbjyIL35V6PEtp3ZQiNeIHeIYUgVC4cq0",
    secure=False,
)

# Define MinIO bucket name
bucket_name = "zenoh" # should be vineyard name

# Define the zenoh topic where the image data will be published
topic = "image_data/*"

# Callback function to handle received image data
def callback(data):
    file_path = str(data.key_expr).split("/", 1)[-1] # Remove topic name
    file_path = file_path.replace("_", "/")  # Replace underscores with slashes
    vineyard_id, block_id, vinerow_id, vine_id, file_name = file_path.split("/")

    image_data = data.payload

    # TODO appednd time stamp to file name not overwrite exixsting files in MinIO and store filename_timestamp.ext or filename/timestamp.ext refrence in orion.
    destination_file_name_minio = block_id + "/" + vinerow_id + "/" + vine_id + "/" + file_name
    photo_id = file_name.split(".")[0]

    # Create or update entity in Orion
    orion_add_image.create_or_update_photo_entity(photo_id, vine_id, vinerow_id, block_id, vineyard_id, file_name)

    # Store files in MinIO. Bucket == vineyard_id, structure blockID/vinerowID/vineID/file.ext
    store_image_in_minio(image_data, destination_file_name_minio)

# Function to store image in MinIO
def store_image_in_minio(image_data, file_name):
    image_stream = BytesIO(image_data)
    image_stream.seek(0)
    minio_client.put_object(bucket_name, file_name, image_stream, len(image_data))
    print(f"Image '{file_name}' stored in MinIO.")

if __name__ == "__main__":
    session = zenoh.open()
    sub = session.declare_subscriber(topic, callback)
    time.sleep(60)

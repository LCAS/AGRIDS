import zenoh
import time
from minio import Minio
from io import BytesIO

# Connect to MinIO
minio_client = Minio(
    "cabbage-xps-8900:9000",
    access_key="KODXtyXxsNTbFrLEitSg",
    secret_key="Ym3Cg3PHbjyIL35V6PEtp3ZQiNeIHeIYUgVC4cq0",
    secure=False,
)

# Define MinIO bucket name
bucket_name = "zenoh"

# Define the topic where the image data will be published
topic = "image_data/*"

# Callback function to handle received image data
def handle_image_data(data):

    file_name = str(data.key_expr).split("/", 1)[-1]
    image_data = data.payload

    store_image_in_minio(image_data, file_name)

# Function to store image in MinIO
def store_image_in_minio(image_data, file_name):
    image_stream = BytesIO(image_data)
    image_stream.seek(0)
    minio_client.put_object(bucket_name, file_name, image_stream, len(image_data))
    print(f"Image '{file_name}' stored in MinIO.")

if __name__ == "__main__":
    session = zenoh.open()
    sub = session.declare_subscriber(topic, handle_image_data)
    time.sleep(60)

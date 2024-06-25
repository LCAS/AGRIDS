import zenoh
import time
from minio import Minio
from minio.error import S3Error
import base64
from PIL import Image
import io
from datetime import datetime

# Connect to MinIO
minio_client = Minio(
    "cabbage-xps-8900:9000",
    access_key="KODXtyXxsNTbFrLEitSg",
    secret_key="Ym3Cg3PHbjyIL35V6PEtp3ZQiNeIHeIYUgVC4cq0",
    secure=False,
)

# Define MinIO bucket name
bucket_name = "zenoh-ros2-test" # Buckets cannot contain underscores _

# Define the topic where the image data will be published
topic = "agrids/image_data"

# Callback function to handle received image data
def handle_image_data(data):
    try:
        # Extract image data from Zenoh message
        image_data = data.payload

        # Convert image data to base64 string
        image_data_base64 = base64.b64decode(image_data)

        # Attempt to open the image with PIL
        image = Image.open(io.BytesIO(image_data_base64))

        timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')

        # Save the image to file
        image_filename = f"image_{timestamp}.jpg"
        #image.save(image_filename)

        store_image_in_minio(image_data_base64, image_filename)
        print(f"Image saved to {bucket_name}/{image_filename}")        
    except Exception as e:
        print(f"Error while decoding image: {e}")

# Function to create bucket if it doesn't exist
def check_bucket_exists(bucket_name):
    try:
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' created successfully.")
        else:
            print(f"Bucket '{bucket_name}' already exists.")
    except S3Error as e:
        print(f"Error while creating bucket: {e}")

# Function to store image in MinIO
def store_image_in_minio(image_data, file_name):
    try:
        # Store the image with appropriate content type
        minio_client.put_object(
            bucket_name,
            file_name,
            io.BytesIO(image_data),
            len(image_data),
            content_type="image/jpeg"  # Set the content type
        )
        
        print(f"Image '{file_name}' stored in MinIO.")
    except Exception as e:
        print(f"Error while storing image: {e}")

if __name__ == "__main__":
    session = zenoh.open()
    sub = session.declare_subscriber(topic, handle_image_data)
    
    check_bucket_exists(bucket_name)
    
    time.sleep(60)

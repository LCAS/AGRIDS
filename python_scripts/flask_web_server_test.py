from flask import Flask, render_template, request
from minio import Minio
from minio.error import S3Error
import requests

# Constants
MINIO_SERVER = "cabbage-xps-8900:9000"
MINIO_ACCESS_KEY = "KODXtyXxsNTbFrLEitSg"
MINIO_SECRET_KEY = "Ym3Cg3PHbjyIL35V6PEtp3ZQiNeIHeIYUgVC4cq0"
MINIO_SECURE = False

FIWARE_ORION_BASE_URL = "http://cabbage-xps-8900:1026/v2/entities/"

app = Flask(__name__)

def initialize_minio_client():
    return Minio(MINIO_SERVER, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=MINIO_SECURE)

def get_fiware_data(entity_id):
    fiware_orion_url = f"{FIWARE_ORION_BASE_URL}{entity_id}"
    response = requests.get(fiware_orion_url)
    if response.status_code == 200:
        fiware_data = response.json()
        return fiware_data
    else:
        return None

@app.route('/', methods=['GET', 'POST'])
def display_image():
    minio_client = initialize_minio_client()
    entity_id = request.args.get('entity_id', 'Vine_1')  # Default to 'Vine_1' if not provided
    try:
        # Get data from Fiware Orion for a specific entity
        fiware_data = get_fiware_data(entity_id)

        if fiware_data is None:
            error_message = f"Entity with ID '{entity_id}' not found in Fiware Orion."
            return render_template('index.html', error_message=error_message)

        # Extract relevant information from Fiware data
        photo_ID = fiware_data.get("photo", {}).get("value")

        # Extract BUCKET_NAME and FILE_NAME from photo_ID
        if photo_ID:
            bucket_file_parts = photo_ID.split('/')
            if len(bucket_file_parts) == 2:
                BUCKET_NAME, FILE_NAME = bucket_file_parts
            else:
                return "Invalid format for photo_ID"

            # Get the presigned URL for the image from MinIO the default expiry time is 7 days (604800 seconds)
            presigned_url = minio_client.presigned_get_object(BUCKET_NAME, FILE_NAME)

            # Extract additional information from Fiware data
            vineyard = fiware_data.get("vineyard", {}).get("value")
            block = fiware_data.get("block", {}).get("value")
            variety = fiware_data.get("variety", {}).get("value")
            grapes = fiware_data.get("grapes", {}).get("value")

            return render_template('index.html',
                                   entity_id=entity_id,
                                   bucket_name=BUCKET_NAME,
                                   file_name=FILE_NAME,
                                   image_url=presigned_url,
                                   vineyard=vineyard,
                                   block=block,
                                   variety=variety,
                                   grapes=grapes)
        else:
            return "photo_ID not found in Fiware data"
    except S3Error as exc:
        return f"Failed to get image. Error: {exc}"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

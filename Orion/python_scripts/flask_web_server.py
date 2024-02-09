from flask import Flask, render_template, request
from minio import Minio
from minio.error import S3Error
import requests

import mongodb_access_vine_data_last_values
import matplotlib.pyplot as plt
from datetime import datetime

# Constants
MINIO_SERVER = "cabbage-xps-8900:9000"
MINIO_ACCESS_KEY = "KODXtyXxsNTbFrLEitSg"
MINIO_SECRET_KEY = "Ym3Cg3PHbjyIL35V6PEtp3ZQiNeIHeIYUgVC4cq0"
MINIO_SECURE = False

FIWARE_ORION_BASE_URL = "http://cabbage-xps-8900:1026/v2/entities/"

app = Flask(__name__)

def initialize_minio_client():
    return Minio(MINIO_SERVER, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=MINIO_SECURE)

def get_fiware_entity_data(entity_id):
    fiware_orion_url = f"{FIWARE_ORION_BASE_URL}{entity_id}"
    response = requests.get(fiware_orion_url)
    if response.status_code == 200:
        fiware_data = response.json()
        return fiware_data
    else:
        return None
    
def get_fiware_data(entity_type_query, entity_type_id, entity_id):
    # Query Orion to get all entities of type "entity_type_query" of type "entity_type_id" with the specified "entity_id"
    fiware_orion_url = f"{FIWARE_ORION_BASE_URL}?type={entity_type_query}&q={entity_type_id}=={entity_id}"

    response = requests.get(fiware_orion_url)
    if response.status_code == 200:
        fiware_data = response.json()
        return fiware_data
    else:
        return None

@app.route('/', methods=['GET', 'POST'])
def display_image():
    minio_client = initialize_minio_client()
    entity_id = request.args.get('entity_id', 'vine001')  # Default to 'Vine_1' if not provided
    try:
        # Get data from Fiware Orion for a specific entity
        fiware_data = get_fiware_entity_data(entity_id)
        fiware_photo_data = get_fiware_data("Photo", "vine_id", entity_id)

        if fiware_data is None:
            error_message = f"Entity with ID '{entity_id}' not found in Fiware Orion."
            return render_template('index.html', error_message=error_message)

        if fiware_photo_data is None:
            error_message = f"Photo with Vine ID '{entity_id}' not found in Fiware Orion."
            return render_template('index.html', error_message=error_message)

        photo_url = [entity['photo']['value'] for entity in fiware_photo_data if 'photo' in entity][0] # Last is index number if vine ID has more than one photo

        # Extract BUCKET_NAME and FILE_PATH from photo_url
        if photo_url:
            # Split the path into two parts
            # File path is vineyard_name/block_name/vine_row_name/vine_name/FILE_PATH.jpg
            path_part = photo_url.split('/')
            BUCKET_NAME = path_part[0]
            FILE_PATH = path_part[1] + "/" + path_part[2] + "/" + path_part[3] + "/" + path_part[4]

            # Get the presigned URL for the image from MinIO the default expiry time is 7 days (604800 seconds)
            presigned_url = minio_client.presigned_get_object(BUCKET_NAME, FILE_PATH)

            # Extract additional information from Fiware data
            #vineyard_id = fiware_data.get("vineyard_id", {}).get("value")
            #block_id = fiware_data.get("block_id", {}).get("value")
            vine_row = fiware_data.get("vine_row_id", {}).get("value")
            variety = fiware_data.get("variety", {}).get("value")
            grapes_number = fiware_data.get("grapes_number", {}).get("value")
            grapes_yield = fiware_data.get("grapes_yield", {}).get("value")
            clone = fiware_data.get("clone", {}).get("value")
            rootstock = fiware_data.get("rootstock", {}).get("value")
            coordinates = fiware_data.get("location", {}).get("value").get("coordinates")
            
            # Get the vine row data from Orion to get Block ID for vine
            fiware_vinerow_data = get_fiware_entity_data(vine_row)
            if fiware_vinerow_data is None:
                error_message = f"Vine Row with ID '{vine_row}' not found in Fiware Orion."
                return render_template('index.html', error_message=error_message)
        
            block_id = fiware_vinerow_data['block_id']['value']

            # Get the block data from Orion to get Vineyard ID for vine
            fiware_block_data = get_fiware_entity_data(block_id)
            if fiware_vinerow_data is None:
                error_message = f"Block with ID '{block_id}' not found in Fiware Orion."
                return render_template('index.html', error_message=error_message)
        
            vineyard_id = fiware_block_data['vineyard_id']['value']

            # Get historic data from MongoDB
            #mongodb_result = mongodb_access_vine_data_last_values.query_recent_values("vine001", "Vine", 10)
            mongodb_result = mongodb_access_vine_data_last_values.query_recent_values(entity_id, "Vine", 10)
            #grapes_number_list = [{result['recvTime'].strftime('%Y-%m-%d %H:%M:%S'), result['attrValue']} for result in mongodb_result]

            results_grape_number = []
            timestamps = []

            for result in mongodb_result:
                results_grape_number.append(result.get('attrValue'))
                timestamps.append(result.get('recvTime'))

            # Create a plot
            plt.figure(figsize=(10, 6))
            plt.plot(timestamps, results_grape_number, marker='o')
            plt.title('Number of Grapes Over Time ' + entity_id)
            plt.xlabel('Timestamp')
            plt.ylabel('Number of Grapes')
            plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability
            plt.tight_layout()

            # Save the plot to a PNG image
            grape_number_plot_path = 'static/plot.png'
            plt.savefig(grape_number_plot_path)
            
            return render_template('index.html',
                                    entity_id=entity_id,
                                    bucket_name=BUCKET_NAME,
                                    file_path=FILE_PATH,
                                    file_name = path_part[4],
                                    image_url=presigned_url,
                                    vineyard_id=vineyard_id,
                                    block_id=block_id,
                                    vine_row=vine_row,
                                    variety=variety,
                                    grapes_number=grapes_number,
                                    grapes_number_list=results_grape_number,
                                    grape_number_plot_path=grape_number_plot_path,
                                    grapes_yield=grapes_yield,
                                    clone=clone,
                                    rootstock=rootstock,
                                    coordinates=coordinates)
        else:
            return "photo_url not found in Fiware data"
    except S3Error as exc:
        return f"Failed to get image. Error: {exc}"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

import requests
import json

def create_photo_entity(photo_id, vine_id, vineyard_name, block_name, vine_row_name, vine_name, file_name):
    # Orion Context Broker endpoint
    ORION_ENDPOINT = 'http://localhost:1026/v2/entities'

    # Constructing the photo URL
    photo_url = f"{vineyard_name}/{block_name}/{vine_row_name}/{vine_name}/{file_name}"

    # Photo entity data
    photo_data = {
        "id": photo_id,
        "type": "Photo",
        "vine_id": {
            "value": vine_id
        },
        "photo": {
            "type": "URL",
            "value": photo_url
        }
    }

    # Convert data to JSON
    photo_json = json.dumps(photo_data)

    # Headers for JSON content
    headers = {'Content-Type': 'application/json'}

    # Create Photo entity in Orion
    response = requests.post(ORION_ENDPOINT, data=photo_json, headers=headers)

    # Print response
    if response.status_code == 201:
        print("Entity " + str(photo_id) + " created successfully")
    else:
        print("Failed to create entity " + str(photo_id) + ". Status code:", response.status_code)
        print("Response:", response.text)

# Example usage:
#create_photo_entity(
#    photo_id="photo001",
#    vine_id="vine001",
#    vineyard_name="vineyard001",
#    block_name="block001",
#    vine_row_name="vinerow001",
#    vine_name="vine001",
#    file_name="photo001.jpg"
#)

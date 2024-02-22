import requests
import json

def create_or_update_photo_entity(photo_id, vine_id, vinerow_id, block_id, vineyard_id, file_name):
    # Orion Context Broker endpoint
    ORION_ENDPOINT = 'http://localhost:1026/v2/entities'

    # Constructing the photo URL
    photo_url = f"{vineyard_id}/{block_id}/{vinerow_id}/{vine_id}/{file_name}"

    # Photo entity data to update
    photo_update_data = {
        "photo": {
            "type": "URL",
            "value": photo_url
        }
    }

    # Photo entity data to create
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
    photo_update_json = json.dumps(photo_update_data)
    photo_json = json.dumps(photo_data)

    # Headers for JSON content
    headers = {'Content-Type': 'application/json'}

    # Check if the entity already exists
    existing_entity_response = requests.get(f"{ORION_ENDPOINT}/{photo_id}")
    if existing_entity_response.status_code == 200:
        # If entity exists, update it
        response = requests.patch(f"{ORION_ENDPOINT}/{photo_id}/attrs", data=photo_update_json, headers=headers)
        if response.status_code == 204:
            print("Entity " + str(photo_id) + " updated successfully")
        else:
            print("Failed to update entity " + str(photo_id) + ". Status code:", response.status_code)
            print("Response:", response.text)
    else:
        # If entity does not exist, create it
        response = requests.post(ORION_ENDPOINT, data=photo_json, headers=headers)
        if response.status_code == 201:
            print("Entity " + str(photo_id) + " created successfully")
        else:
            print("Failed to create entity " + str(photo_id) + ". Status code:", response.status_code)
            print("Response:", response.text)

# Example usage:
#create_or_update_photo_entity(
#    photo_id="photo001",
#    vine_id="vine001",
#    vineyard_name="vineyard001",
#    block_name="block001",
#    vine_row_name="vinerow001",
#    vine_name="vine001",
#    file_name="photo001.jpg"
#)

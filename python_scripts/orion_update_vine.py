import requests
import json

ORION_ENDPOINT_BASE = 'http://localhost:1026/v2/entities/'

# Vine entity ID
vine_entity_id = 'vine001'

ORION_ENDPOINT = f'{ORION_ENDPOINT_BASE}{vine_entity_id}'

updated_vine_data = {
    "variety": {
        "value": "Cabernet Sauvignon",
        "type": "String"
    },
    "clone": {
        "value": "Cabernet Clone", 
        "type": "String"
    },
    "rootstock": {
        "value": "101-14",
        "type": "String"
    },
    "location": {
        "type": "geo:json",
        "value": {
            "type": "Point",
            "coordinates": [53.227216007632244, -0.5493656119079906]
        }
    }
}

# Convert updated data to JSON
updated_vine_json = json.dumps(updated_vine_data)

# Headers for JSON content
headers = {'Content-Type': 'application/json'}

# Update Vine entity in Orion using PATCH request
response = requests.patch(ORION_ENDPOINT, data=updated_vine_json, headers=headers)

# Print response
if response.status_code == 204:
    print("Entity updated successfully")
else:
    print("Failed to update entity. Status code:", response.status_code)
    print("Response:", response.text)

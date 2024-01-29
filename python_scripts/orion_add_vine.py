import requests
import json

# Orion Context Broker endpoint
ORION_ENDPOINT = 'http://localhost:1026/v2/entities'

# folder and file names for objects (photos)  stored in minio storage
# fodler structure vineyard_name/block_name/vine_row_name/vine_name/file_name.jpg
# to upload to minio bucket name = vineyard_name and object name = block_name/vine_row_name/vine_name/file_name.jpg
vineyard_name = "vineyard001"
block_name = "block001"
vine_row_name = "vinerow001"
vine_name = "vine002"
file_name = "photo001.jpg"

# Vine entity data
vine_data = {
    "id": "vine002",
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
        "value": "Vine 2",
        "type": "String"
    },
    "variety": {
        "value": "Merlot",
        "type": "String"
    },
    "clone": {
        "value": "Chardonnay",
        "type": "String"
    },
    "rootstock": {
        "value": "3309C",
        "type": "String"
    },
    "location": {
        "type": "geo:json",
        "value": {
            "type": "Point",
            "coordinates": [53.227216007632244, -0.5493656119079906]
        }
    },
    "photo": {
        "type": "URL",
        "value": f"{vineyard_name}/{block_name}/{vine_row_name}/{vine_name}/{file_name}"
    }
}

# Convert data to JSON
vine_json = json.dumps(vine_data)

# Headers for JSON content
headers = {'Content-Type': 'application/json'}

# Create Vine entity in Orion
response = requests.post(ORION_ENDPOINT, data=vine_json, headers=headers)

# Print response
if response.status_code == 201:
    print("Entity created successfully")
else:
    print("Failed to create entity. Status code:", response.status_code)
    print("Response:", response.text)

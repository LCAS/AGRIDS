import requests
import json

# Orion Context Broker endpoint
ORION_ENDPOINT = 'http://localhost:1026/v2/entities'

# Block entity data
block_data = {
    "id": "block001",
    "type": "Block",
    "vineyard_id": {
        "value": "vineyard001",
        "type": "String"
    },
    "user_defined_id": {
        "value": "North Block",
        "type": "String"
    },
    "row_spacing_m": {
        "value": 1.5,
        "type": "Float"
    },
    "vine_spacing_m": {
        "value": 1.0,
        "type": "Float"
    },
    "date_start": {
        "value": "2024-01-01T00:00:00Z",
        "type": "DateTime"
    },
    "date_start": {
        "value": "2024-12-31T00:00:00Z",
        "type": "DateTime"
    },
    "geom": {
        "type": "geo:json",
        "value": {
            "type": "MultiPoint",
            "coordinates": 
            [53.227176516724036, -0.5490537449585962],
            [53.22715082571518, -0.5489410921784628],
            [53.22712754322504, -0.5491033658260358],
            [53.227084189589014, -0.5489384099694119]
        }
    },
    "hasVineRow": {
        "type": "Relationship",
        "value": ["vinerow001", "vinerow002"]
    }
}

# Convert data to JSON
block_json = json.dumps(block_data)

# Headers for JSON content
headers = {'Content-Type': 'application/json'}

# Create Block entity in Orion
response = requests.post(ORION_ENDPOINT, data=block_json, headers=headers)

# Print response
if response.status_code == 201:
    print("Entity created successfully")
else:
    print("Failed to create entity. Status code:", response.status_code)
    print("Response:", response.text)

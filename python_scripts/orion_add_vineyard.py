import requests
import json

# Orion Context Broker endpoint
ORION_ENDPOINT = 'http://localhost:1026/v2/entities'

# Vineyard entity data
vineyard_data = {
    "id": "vineyard001",
    "type": "Vineyard",
    "name": {
        "value": "Lincoln Vineyard",
        "type": "String"
    },
    "street_address": {
        "value": "Univeristy of Lincoln, Brayford Pool, Lincoln, LN6 7TS",
        "type": "String"
    },
    "owner": {
        "value": "University of Lincoln",
        "type": "String"
    },
    "geom": {
        "type": "geo:json",
        "value": {
            "type": "MultiPoint",
            "coordinates": 
            [53.22705288052429, -0.5491956099145128],
            [53.22721987218854, -0.5493028982765445],
            [53.227284099578306, -0.5489220245913319],
            [53.226951721795565, -0.5487396343758779]
        }
    },
    "hasBlock": {
        "type": "Relationship",
        "object": "Block",
        "value": ["block001", "block002"]
    }
}

# Convert data to JSON
vineyard_json = json.dumps(vineyard_data)

# Headers for JSON content
headers = {'Content-Type': 'application/json'}

# Create Vineyard entity in Orion
response = requests.post(ORION_ENDPOINT, data=vineyard_json, headers=headers)

# Print response
if response.status_code == 201:
    print("Entity created successfully")
else:
    print("Failed to create entity. Status code:", response.status_code)
    print("Response:", response.text)

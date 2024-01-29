import requests
import json

# Orion Context Broker endpoint
ORION_ENDPOINT = 'http://localhost:1026/v2/entities'

# VineRow entity data
vine_row_data = {
    "id": "vinerow001", 
    "type": "VineRow",
    "block_id": {
        "value": "block001",
        "type": "String"
    },
    "vineyard_id": {
        "value": "vineyard001",
        "type": "String"
    },
    "user_defined_id": {
        "value": "Vine Row 1",
        "type": "String"
    },
    "orientation": {
        "value": 45,
        "type": "Float"
    },
    "orientation": {
        "value": 45,
        "type": "Float"
    },
    "geom": {
        "type": "geo:json",
        "value": {
            "type": "MultiLineString",
            "coordinates": 
            [ [53.227176516724036, -0.5490537449585962], [53.22716326979953, -0.5488767191612437]],
            [53.22715082571518, -0.5489410921784628, [53.22712834606973, -0.5489840075232755]],
            [53.22712754322504, -0.5491033658260358, [53.22705608998665, -0.548782841844466]]
        }
    },
    "hasVine": {
        "type": "Relationship",
        "value": ["vine001", "vine002"] 
    }
}

# Convert data to JSON
vine_row_json = json.dumps(vine_row_data)

# Headers for JSON content
headers = {'Content-Type': 'application/json'}

# Create VineRow entity in Orion
response = requests.post(ORION_ENDPOINT, data=vine_row_json, headers=headers)

# Print response
if response.status_code == 201:
    print("Entity created successfully")
else:
    print("Failed to create entity. Status code:", response.status_code)
    print("Response:", response.text)

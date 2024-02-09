import requests
import json

def create_block_entity(block_id, vineyard_id, user_defined_id, row_spacing_m, vine_spacing_m, date_start, date_end, geom_coordinates):
    # Orion Context Broker endpoint
    ORION_ENDPOINT = 'http://localhost:1026/v2/entities'

    # Block entity data
    block_data = {
        "id": block_id,
        "type": "Block",
        "vineyard_id": {
            "value": vineyard_id,
            "type": "String"
        },
        "user_defined_id": {
            "value": user_defined_id,
            "type": "String"
        },
        "row_spacing_m": {
            "value": row_spacing_m,
            "type": "Float"
        },
        "vine_spacing_m": {
            "value": vine_spacing_m,
            "type": "Float"
        },
        "date_start": {
            "value": date_start,
            "type": "DateTime"
        },
        "date_end": {
            "value": date_end,
            "type": "DateTime"
        },
        "geom": {
            "type": "geo:json",
            "value": {
                "type": "MultiPoint",
                "coordinates": geom_coordinates
            }
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
        print("Entity " + str(block_id) + " created successfully")
    else:
        print("Failed to create entity " + str(block_id) + ". Status code:", response.status_code)
        print("Response:", response.text)

# Example usage:
#create_block_entity(
#    block_id="block001",
#    vineyard_id="vineyard001",
#    user_defined_id="North Block",
#    row_spacing_m=1.5,
#    vine_spacing_m=1.0,
#    date_start="2024-01-01T00:00:00Z",
#    date_end="2024-12-31T00:00:00Z",
#    geom_coordinates=[
#        [53.227176516724036, -0.5490537449585962],
#        [53.22715082571518, -0.5489410921784628],
#        [53.22712754322504, -0.5491033658260358],
#        [53.227084189589014, -0.5489384099694119]
#    ]
#)

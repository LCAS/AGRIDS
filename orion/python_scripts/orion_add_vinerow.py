import requests
import json

def create_vine_row_entity(vine_row_id, block_id, user_defined_id, orientation, geom_coordinates):
    # Orion Context Broker endpoint
    ORION_ENDPOINT = 'http://localhost:1026/v2/entities'

    # VineRow entity data
    vine_row_data = {
        "id": vine_row_id,
        "type": "VineRow",
        "block_id": {
            "value": block_id,
            "type": "String"
        },
        "user_defined_id": {
            "value": user_defined_id,
            "type": "String"
        },
        "orientation": {
            "value": orientation,
            "type": "Float"
        },
        "geom": {
            "type": "geo:json",
            "value": {
                "type": "MultiLineString",
                "coordinates": geom_coordinates
            }
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
        print("Entity " + str(vine_row_id) + " created successfully")
    else:
        print("Failed to create entity " + str(vine_row_id) + ". Status code:", response.status_code)
        print("Response:", response.text)

# Example usage:
#create_vine_row_entity(
#    vine_row_id="vinerow001", 
#    block_id="block001",
#    user_defined_id="Vine Row 1",
#    orientation=45,
#    geom_coordinates=[
#        [[53.227176516724036, -0.5490537449585962], [53.22716326979953, -0.5488767191612437]],
#        [[53.22715082571518, -0.5489410921784628], [53.22712834606973, -0.5489840075232755]],
#        [[53.22712754322504, -0.5491033658260358], [53.22705608998665, -0.548782841844466]]
#    ]
#)

import requests
import json

def create_vine_entity(vine_id, vine_row_id, user_defined_id, variety, clone, rootstock, location_coordinates, grapes_number, grapes_yield):
    # Orion Context Broker endpoint
    ORION_ENDPOINT = 'http://localhost:1026/v2/entities'

    # Vine entity data
    vine_data = {
        "id": vine_id,
        "type": "Vine",
        "vine_row_id": {
            "value": vine_row_id,
            "type": "String"
        },
        "user_defined_id": {
            "value": user_defined_id,
            "type": "String"
        },
        "variety": {
            "value": variety,
            "type": "String"
        },
        "clone": {
            "value": clone,
            "type": "String"
        },
        "rootstock": {
            "value": rootstock,
            "type": "String"
        },
        "location": {
            "type": "geo:json",
            "value": {
                "type": "Point",
                "coordinates": location_coordinates
            }
        },
        "grapes_number": {
            "value": grapes_number,
            "type": "Integer"
        },
        "grapes_yield": {
            "value": grapes_yield,
            "type": "Float"
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
        print("Entity " + str(vine_id) + " created successfully")
        return "Entity " + str(vine_id) + " created successfully"
    else:
        print("Failed to create entity " + str(vine_id) + ". Status code:", str(response.status_code))
        print("Response:", response.text)
        return "Failed to create entity " + str(vine_id) + ". Status code:" + str(response.status_code) + " Response:" + str(response.text)

# Example usage:
#create_vine_entity(
#    vine_id="vine001",
#    vine_row_id="vinerow001",
#    user_defined_id="Vine 1",
#    variety="Merlot",
#    clone="Chardonnay",
#    rootstock="3309C",
#    location_coordinates=[53.227216007632244, -0.5493656119079906],
#    grapes_number=5,
#    grapes_yield=4.8
#)

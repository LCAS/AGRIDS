import requests
import json

def create_vineyard_entity(vineyard_id, vineyard_name, street_address, owner, geom_coordinates):
    # Orion Context Broker endpoint
    ORION_ENDPOINT = 'http://localhost:1026/v2/entities'

    # Vineyard entity data
    vineyard_data = {
        "id": vineyard_id,
        "type": "Vineyard",
        "name": {
            "value": vineyard_name,
            "type": "String"
        },
        "street_address": {
            "value": street_address,
            "type": "String"
        },
        "owner": {
            "value": owner,
            "type": "String"
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
    vineyard_json = json.dumps(vineyard_data)

    # Headers for JSON content
    headers = {'Content-Type': 'application/json'}

    # Create Vineyard entity in Orion
    response = requests.post(ORION_ENDPOINT, data=vineyard_json, headers=headers)

    # Print response
    if response.status_code == 201:
        print("Entity " + str(vineyard_id) + " created successfully")
    else:
        print("Failed to create entity " + str(vineyard_id) + ". Status code:", response.status_code)
        print("Response:", response.text)

# Example usage:
#create_vineyard_entity(
#    vineyard_id="vineyard001",
#    vineyard_name="Lincoln Vineyard",
#    street_address="University of Lincoln, Brayford Pool, Lincoln, LN6 7TS",
#    owner="University of Lincoln",
#    geom_coordinates=[
#        [53.22705288052429, -0.5491956099145128],
#        [53.22721987218854, -0.5493028982765445],
#        [53.227284099578306, -0.5489220245913319],
#        [53.226951721795565, -0.5487396343758779]
#    ]
#)

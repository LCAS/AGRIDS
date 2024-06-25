import requests
import json
import uuid

def create_vineyard_entity(vineyard_id, vineyard_name, street_address, owner, geom_coordinates):
    # Orion Context Broker endpoint
    ORION_ENDPOINT = 'http://localhost:1026/v2/entities'

    # Entity data
    data = {
        "id": str(uuid.uuid4()),
        "type": "Vineyard",
        "vineyard_id": {
            "value": vineyard_id,
            "type": "String"
        },
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
    data_json = json.dumps(data)

    # Headers for JSON content
    headers = {'Content-Type': 'application/json'}

    # Create Vine entity in Orion
    response = requests.post(ORION_ENDPOINT, data=data_json, headers=headers)

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

# create_vineyard_entity(
#    vineyard_id="jojo",
#    vineyard_name="JoJos Vineyard",
#    street_address="Russells Water, Henley-on-Thames, RG9 6EU",
#    owner="Ian Beecher-Jones",
#    geom_coordinates=[
#        [-0.9788445498611473, 51.59743741002565],
#        [-0.9770441056098098, 51.59724235040105],
#        [-0.9755356595482222, 51.59589630833273],
#        [-0.9773805584763098, 51.595171685867975],
#        [-0.9786402550768042, 51.59608874584751]
#    ]
# )

# create_vineyard_entity(
#    vineyard_id="harrowandhope",
#    vineyard_name="Harrow and Hope",
#    street_address="Marlow Winery, Pump Lane North, Marlow, SL7 3RD",
#    owner="Henry Laithwaite",
#    geom_coordinates=[
#        [51.588715894675715, -0.7619415128540115],
#        [51.58645668558797, -0.7587403960645095],
#        [51.58497206846389, -0.7612351950660405],
#        [51.58459605910814, -0.7625735525334627],
#        [51.58775006546342, -0.7648225027142868]
#    ]
# )
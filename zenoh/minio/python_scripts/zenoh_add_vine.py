import requests
import json

def store_vine_data(vine_id, vine_row_id, user_defined_id, variety, clone, rootstock, location_coordinates, grapes_number, grapes_yield):

    # URL endpoint
    # port is set in zenoh_minio.json5 file
    # "s3/example" is the key expression the storage subscribes to and is set in zenoh_minio.json5 file 
    # /id is the id of the data stored
    url = 'http://localhost:10000/s3/example/' + vine_id

    # JSON data to be sent in the request body
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

    # Headers
    headers = {
        'content-type': 'application/json'
    }

    # Making the PUT request
    response = requests.put(url, headers=headers, data=json.dumps(vine_data))

    # Checking response status
    if response.status_code == 200:
        print("Request successful")
    else:
        print("Request failed with status code:", response.status_code)

store_vine_data(
    vine_id="vine001",
    vine_row_id="vinerow001",
    user_defined_id="Vine 1",
    variety="Merlot",
    clone="Chardonnay",
    rootstock="3309C",
    location_coordinates=[53.227216007632244, -0.5493656119079906],
    grapes_number=5,
    grapes_yield=4.8
)
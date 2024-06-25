import requests
import json
import uuid

def create_line_feature_entity(name, category, class_string, vineyard_id, geom_coordinates):
    # Orion Context Broker endpoint
    ORION_ENDPOINT = 'http://localhost:1026/v2/entities'

    # Entity data
    data = {
        "id": str(uuid.uuid4()),
        "type": "line",
        "name": {
            "value": name,
            "type": "String"
        },
        "category": {
            "value": category,
            "type": "String"
        },
        "class": {
            "value": class_string,
            "type": "String"
        },
        "vineyard_id": {
            "value": vineyard_id,
            "type": "String"
        },
        "geom": {
            "type": "geo:json",
            "value": {
                "type": "LineString",
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
        print("Entity " + str(name) + " created successfully")
    else:
        print("Failed to create entity " + str(name) + ". Status code:", response.status_code)
        print("Response:", response.text)

# Example usage:
#create_line_feature_entity(    
#    name = "Drainage Lines", 
#    category = "plant_equipment", 
#    class_string = "drainage_line", 
#    vineyard_id = "jojo", 
#    geom_coordinates = [
#        [-0.9759959481218061,51.59630503810885],
#        [-0.9761386450103657,51.59633913158373],
#        [-0.9763106130544656,51.596427774497585],
#        [-0.9763362253174535,51.596491415457336]
#    ]
#)

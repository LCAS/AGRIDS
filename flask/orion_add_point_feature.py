import requests
import json
import uuid

def create_point_feature_entity(name, category, class_string, vineyard_id, location_coordinates):
    # Orion Context Broker endpoint
    ORION_ENDPOINT = 'http://localhost:1026/v2/entities'

    # Entity data
    data = {
        "id": str(uuid.uuid4()),
        "type": "point",
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
        "location": {
            "type": "geo:json",
            "value": {
                "type": "Point",
                "coordinates": location_coordinates
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
#create_point_feature_entity(    
#    name = "Entrance", 
#    category = "fixed_structure", 
#    class_string = "entrance_exit", 
#    vineyard_id = "jojo", 
#    location_coordinates = [-0.9760, 51.5962]
#)

# create_point_feature_entity(    
#    name = "Entrance", 
#    category = "fixed_structure", 
#    class_string = "entrance_exit", 
#    vineyard_id = "harrowandhope", 
#    location_coordinates = [-0.7609291143207004, 51.58778425392286]
# )

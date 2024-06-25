import requests
import json
import uuid

def create_polygon_feature_entity(name, category, class_string, vineyard_id, geom_coordinates):
    # Orion Context Broker endpoint
    ORION_ENDPOINT = 'http://localhost:1026/v2/entities'

    # Entity data
    data = {
        "id": str(uuid.uuid4()),
        "type": "polygon",
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
        print("Entity " + str(name) + " created successfully")
    else:
        print("Failed to create entity " + str(name) + ". Status code:", response.status_code)
        print("Response:", response.text)

# Example usage:
#create_polygon_feature_entity(    
#    name = "Building", 
#    category = "fixed_structure", 
#    class_string = "building", 
#    vineyard_id = "jojo", 
#    geom_coordinates = [
#        [-0.9766262528260654,51.59662311506793],
#        [-0.976506498599889,51.596529241115036],
#        [-0.9763867443751337,51.59643536696811],
#        [-0.9763525288811365,51.59646016393137],
#        [-0.9765464166757454,51.596640827112594],
#        [-0.9766262528260654,51.59662311506793]
#    ]
#)

# create_polygon_feature_entity(    
#    name = "Building", 
#    category = "fixed_structure", 
#    class_string = "building", 
#    vineyard_id = "harrowandhope", 
#    geom_coordinates = [
#        [-0.7613523584324966, 51.58807783670938],
#        [-0.7612138331526814, 51.587961536639064],
#        [-0.7613454369640139, 51.58789578928606],
#        [-0.761488159321504, 51.588015474928234],
#        [-0.7613523584324966, 51.58807783670938]
#    ]
# )

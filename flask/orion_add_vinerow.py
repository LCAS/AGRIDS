import requests
import json

def create_vine_row_entity(vine_row_id, block_id, vineyard_id, user_defined_id, orientation, category, class_string, vine_spacing, under_vine_width, anchor_post_distance, geom_coordinates):
    # Orion Context Broker endpoint
    ORION_ENDPOINT = 'http://localhost:1026/v2/entities'

    # VineRow entity data
    vine_row_data = {
        "id": vine_row_id,
        "type": "VineRow",
        "vineyard_id": {
            "value": vineyard_id,
            "type": "String"
        },
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
        "category": {
            "value": category,
            "type": "String"
        },
        "class": {
            "value": class_string,
            "type": "String"
        },
        "vine_spacing": {
            "value": vine_spacing,
            "type": "Float"
        },
        "under_vine_width": {
            "value": under_vine_width,
            "type": "Float"
        },
        "anchor_post_distance": {
            "value": anchor_post_distance,
            "type": "Float"
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
    vine_row_json = json.dumps(vine_row_data)

    # Headers for JSON content
    headers = {'Content-Type': 'application/json'}

    # Create VineRow entity in Orion
    response = requests.post(ORION_ENDPOINT, data=vine_row_json, headers=headers)

    # Print response
    if response.status_code == 201:
        print("Entity " + str(vine_row_id) + " created successfully")
        return "Entity " + str(vine_row_id) + " created successfully"
    else:
        print("Failed to create entity " + str(vine_row_id) + ". Status code:", str(response.status_code))
        print("Response:", response.text)
        return "Failed to create entity " + str(vine_row_id) + ". Status code:" + str(response.status_code) + " Response:" + str(response.text)

# Example usage:
#create_vine_row_entity(
#    vine_row_id="vinerow007", 
#    block_id="block001",
#    user_defined_id="Vine Row 7",
#    orientation=45,
#    geom_coordinates=[
#        [53.227793225574686, -0.548744542980351], 
#        [53.22769206979758, -0.5480900758341881],
#        [53.22755076896741, -0.5475429015848795],
#        [53.22747851377061, -0.5477467510708004],
#        [53.22749457067276, -0.5481544485776082],
#        [53.227672798667854, -0.5488330544585053]
#    ]
#)

# create_vine_row_entity(
#     vine_row_id = "harrowandhope_vine_row_1", 
#     block_id = "block_1", 
#     vineyard_id = "harrowandhope", 
#     user_defined_id = "row_1", 
#     orientation = 0, 
#     category = "vineyard", 
#     class_string = "row", 
#     vine_spacing = 1, 
#     under_vine_width = 0.5, 
#     anchor_post_distance = 2, 
#     geom_coordinates = [
#         [-0.7629570606813445, 51.587804669051025], 
#         [-0.7630703880361125, 51.587477099294915]
#     ]
# )
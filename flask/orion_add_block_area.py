import requests
import json
import uuid

def create_block_aera_entity(block_id, vineyard_id, user_defined_id, name, date_start, date_end, geom_coordinates):
    # Orion Context Broker endpoint
    ORION_ENDPOINT = 'http://localhost:1026/v2/entities'

    # Block entity data
    block_data = {
        "id": block_id,
        "type": "BlockArea",
        "vineyard_id": {
            "value": vineyard_id,
            "type": "String"
        },
        "user_defined_id": {
            "value": user_defined_id,
            "type": "String"
        },
        "name": {
            "value": name,
            "type": "String"
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
        return "Entity " + str(block_id) + " created successfully"
    else:
        print("Failed to create entity " + str(block_id) + ". Status code:", str(response.status_code))
        print("Response:", response.text)
        return "Failed to create entity " + str(block_id) + ". Status code:" + str(response.status_code) + " Response:" + str(response.text)

# Example usage:
create_block_aera_entity(
    block_id = str(uuid.uuid4()), 
    vineyard_id = "jojo", 
    user_defined_id = "South Block",
    name = "South Block",
    date_start = "2024-01-01T00:00:00Z", 
    date_end = "2024-12-31T00:00:00Z", 
    geom_coordinates=[
       [-0.9768514621432871, 51.59634024768235],
       [-0.9764900569160204, 51.59621866402969],
       [-0.9761876887723417, 51.59596522049293],
       [-0.9763278230639401, 51.59589934337876],
       [-0.9762511279451473, 51.59582934884034],
       [-0.976796251188432, 51.59557267727922],
       [-0.9767766044089683, 51.59555476820606],
       [-0.977373764049446, 51.595276030174375],
       [-0.9780719352931726, 51.59576885043242],
       [-0.9768514621432871, 51.59634024768235]
   ]
)

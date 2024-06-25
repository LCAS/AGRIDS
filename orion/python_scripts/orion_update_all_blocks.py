import requests
import json

# Orion endpoint base URL
ORION_ENDPOINT_BASE = 'http://localhost:1026/v2/entities/'

# Parameters for pagination
limit = 1000
offset = 0

# Data to add new attributes
updated_data = {
    "vine_spacing": {
        "value": 1.0,
        "type": "Float"
    },
    "under_vine_width": {
        "value": 0.5,
        "type": "Float"
    },
    "anchor_post_distance": {
        "value": 1.0,
        "type": "Float"
    }
}

# Convert updated data to JSON
updated_json = json.dumps(updated_data)

# Headers for JSON content
headers = {'Content-Type': 'application/json'}

while True:
    # Endpoint to list entities with pagination
    ORION_LIST_ENTITIES_ENDPOINT = f'{ORION_ENDPOINT_BASE}?type=Block&limit={limit}&offset={offset}'
    
    # Fetch entities with pagination
    response = requests.get(ORION_LIST_ENTITIES_ENDPOINT)
    
    if response.status_code == 200:
        vine_rows = response.json()
        
        if not vine_rows:
            # No more entities to process
            break
        
        for vine_row in vine_rows:
            entity_id = vine_row['id']
            ORION_ENDPOINT = f'{ORION_ENDPOINT_BASE}{entity_id}/attrs'
            update_response = requests.post(ORION_ENDPOINT, data=updated_json, headers=headers)
            
            if update_response.status_code == 204:
                print(f"Entity {entity_id} updated successfully")
            else:
                print(f"Failed to update entity {entity_id}. Status code:", update_response.status_code)
                print("Response:", update_response.text)
        
        # Increment offset for the next batch of entities
        offset += limit
    else:
        print("Failed to fetch entities. Status code:", response.status_code)
        print("Response:", response.text)
        break

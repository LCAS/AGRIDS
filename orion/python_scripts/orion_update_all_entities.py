import requests
import json
import re

# Orion endpoint base URL
ORION_ENDPOINT_BASE = 'http://localhost:1026/v2/entities/'

# Parameters for pagination
limit = 1000
offset = 0

# Data to add new attributes
updated_data = {
    "vineyard_id": {
        "value": "jojo",
        "type": "String"
    }
}

# Convert updated data to JSON
updated_data_json = json.dumps(updated_data)

# Headers for JSON content
headers = {'Content-Type': 'application/json'}

# Regular expression to match UUIDs
uuid_regex = re.compile(
    r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
)

while True:
    # Endpoint to list entities with pagination (no filtering by type)
    ORION_LIST_ENTITIES_ENDPOINT = f'{ORION_ENDPOINT_BASE}?limit={limit}&offset={offset}'
    
    # Fetch entities with pagination
    response = requests.get(ORION_LIST_ENTITIES_ENDPOINT)
    
    if response.status_code == 200:
        entities = response.json()
        
        if not entities:
            # No more entities to process
            break
        
        for entity in entities:
            entity_id = entity['id']
            
            # Check if the entity ID does not match the UUID format
            #if not uuid_regex.match(entity_id):
            if uuid_regex.match(entity_id):
                ORION_ENDPOINT = f'{ORION_ENDPOINT_BASE}{entity_id}/attrs'
                update_response = requests.post(ORION_ENDPOINT, data=updated_data_json, headers=headers)
                
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

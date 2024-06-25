import requests

# Orion endpoint base URL
ORION_ENDPOINT_BASE = 'http://localhost:1026/v2/entities/'

# Parameters for pagination
limit = 1000
offset = 0

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
        
        # Filter entities that lack the 'vineyard_id' attribute
        entities_without_vineyard_id = [entity for entity in entities if 'vineyard_id' not in entity]
        
        for entity in entities_without_vineyard_id:
            print(entity['id'])  # Print the IDs of entities without 'vineyard_id'
        
        # Increment offset for the next batch of entities
        offset += limit
    else:
        print("Failed to fetch entities. Status code:", response.status_code)
        print("Response:", response.text)
        break

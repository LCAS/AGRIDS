import requests

# Function to find all vine_ids given a block_id
def find_vine_ids_in_block(entity_type_vine, entity_type_vinerow, block_id):
    # Orion Context Broker API base URL
    FIWARE_ORION_BASE_URL = "http://localhost:1026/v2/entities/"

    try:
        # Query Orion to get all entities of type "VineRow" with the specified block_id
        fiware_orion_url_vinerow = f"{FIWARE_ORION_BASE_URL}?type={entity_type_vinerow}&q=block_id=={block_id}"
        vinerow_response = requests.get(fiware_orion_url_vinerow)

        if vinerow_response.status_code == 200:
            vinerow_data = vinerow_response.json()
            vine_data_list = []
            # For each VineRow, query Orion to get all entities of type "Vine" with the vinerow_id
            for vinerow_entity in vinerow_data:
                vinerow_id = vinerow_entity['id']
                fiware_orion_url_vine = f"{FIWARE_ORION_BASE_URL}?type={entity_type_vine}&q=vinerow_id=={vinerow_id}"
                vine_response = requests.get(fiware_orion_url_vine)
                if vine_response.status_code == 200:
                    vine_data = vine_response.json()
                    vine_ids = [entity['id'] for entity in vine_data]
                    # Append each (vine_id, vinerow_id) tuple to the list
                    vine_data_list.extend([(vine_id, vinerow_id) for vine_id in vine_ids])
                else:
                    print(f"Failed to retrieve vine data for vinerow_id {vinerow_id}. Status code: {vine_response.status_code}")
            return vine_data_list
        else:
            print(f"Failed to retrieve vinerow data. Status code: {vinerow_response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

# Example usage
entity_type_vine = "Vine"
entity_type_vinerow = "VineRow"
block_id = "block001"

vine_data_list = find_vine_ids_in_block(entity_type_vine, entity_type_vinerow, block_id)
if vine_data_list is not None:
    print("Vine IDs in " + block_id + ":")
    for vine_id, vinerow_id in vine_data_list:
        print(f"Vine ID: {vine_id}, VineRow ID: {vinerow_id}")

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
            vine_row_ids = set()
            total_vine_count = 0
            total_grapes_count = 0
            total_vine_row = 0

            # For each VineRow, query Orion to get all entities of type "Vine" with the vine_row_id
            for vinerow_entity in vinerow_data:
                vine_row_id = vinerow_entity['id']
                vine_row_ids.add(vine_row_id)  # Add vine row ID to set
                total_vine_row += 1  # Increment the total vine row count
                fiware_orion_url_vine = f"{FIWARE_ORION_BASE_URL}?type={entity_type_vine}&q=vine_row_id=={vine_row_id}"
                vine_response = requests.get(fiware_orion_url_vine)
                if vine_response.status_code == 200:
                    vine_data = vine_response.json()
                    vine_ids = [entity['id'] for entity in vine_data]

                    # Accumulate the total number of vines
                    total_vine_count += len(vine_ids)

                    # Accumulate the total number of grapes
                    for vine_entity in vine_data:
                        grapes_number = vine_entity.get('grapes_number', {}).get("value")
                        total_grapes_count += int(grapes_number)

                    # Append each (vine_id, vine_row_id) tuple to the list
                    vine_data_list.extend([(vine_id, vine_row_id) for vine_id in vine_ids])
                else:
                    print(f"Failed to retrieve vine data for vine_row_id {vine_row_id}. Status code: {vine_response.status_code}")

            return vine_data_list, total_vine_count, total_vine_row, list(vine_row_ids), total_grapes_count  # Return vine data list, total vine count, total vine row count, vine row IDs, and total grapes count
        else:
            print(f"Failed to retrieve vinerow data. Status code: {vinerow_response.status_code}")
            return None, None, None, None, None

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None, None, None, None, None

# Example usage
#entity_type_vine = "Vine"
#entity_type_vinerow = "VineRow"
#block_id = "block001"

#vine_data_list, total_vine_count, total_vine_row, vine_row_ids, total_grapes_count = find_vine_ids_in_block(entity_type_vine, entity_type_vinerow, block_id)
#if vine_data_list is not None:
#    print("Vine IDs in " + block_id + ":")
#    for vine_id, vine_row_id in vine_data_list:
#        print(f"Vine ID: {vine_id}, VineRow ID: {vine_row_id}")
#    print(f"Total number of vines in {block_id}: {total_vine_count}")
#    print(f"Total number of vine rows in {block_id}: {total_vine_row}")
#    print(f"Vine row IDs in {block_id}: {vine_row_ids}")
#    print(f"Total number of grapes in {block_id}: {total_grapes_count}")

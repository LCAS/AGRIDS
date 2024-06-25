import requests

# Function to find vine ids, total number of grapes, and total number of vines given a vine_row_id
def find_vine_ids_grapes_and_total_vines_in_row(entity_type_vine, vine_row_id):
    # Orion Context Broker API base URL
    FIWARE_ORION_BASE_URL = "http://localhost:1026/v2/entities/"

    try:
        # Query Orion to get all entities of type "Vine" with the specified vine_row_id
        fiware_orion_url_vine = f"{FIWARE_ORION_BASE_URL}?type={entity_type_vine}&q=vine_row_id=={vine_row_id}"
        vine_response = requests.get(fiware_orion_url_vine)

        if vine_response.status_code == 200:
            vine_data = vine_response.json()
            vine_ids = [entity['id'] for entity in vine_data]
            total_grapes_count = sum(int(entity.get('grapes_number', {}).get("value", 0)) for entity in vine_data)
            total_vines = len(vine_ids)
            return vine_ids, total_grapes_count, total_vines
        else:
            print(f"Failed to retrieve vine data for vine_row_id {vine_row_id}. Status code: {vine_response.status_code}")
            return None, None, None

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None, None, None

# Example usage
#entity_type_vine = "Vine"
#vine_row_id = "vinerow001"

#vine_ids, total_grapes_count, total_vines = find_vine_ids_grapes_and_total_vines_in_row(entity_type_vine, vine_row_id)
#if vine_ids is not None:
#    print("Vine IDs in " + vine_row_id + ":")
#    for vine_id in vine_ids:
#        print(f"Vine ID: {vine_id}")
#    print(f"Total number of vines in {vine_row_id}: {total_vines}")
#    print(f"Total number of grapes in {vine_row_id}: {total_grapes_count}")

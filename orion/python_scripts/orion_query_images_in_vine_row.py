import requests

# Find all vines in a specific vinerow
def find_vines_in_vinerow(entity_type, vine_row_id):
    # Orion Context Broker API base URL
    FIWARE_ORION_BASE_URL = "http://localhost:1026/v2/entities/"

    try:
        # Query Orion to get all entities of type Vine with the specified vine_row_id
        fiware_orion_url = f"{FIWARE_ORION_BASE_URL}?type={entity_type}&q=vine_row_id=={vine_row_id}"
    
        vine_response = requests.get(fiware_orion_url)

        if vine_response.status_code == 200:
            vine_data = vine_response.json()
            vine_ids = [entity['id'] for entity in vine_data]
            return vine_ids
        else:
            print(f"Failed to retrieve vine data. Status code: {vine_response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

# Find all photo URLs associated with vines from first query
def find_photos_for_vines(entity_type, vine_id):
    # Orion Context Broker API base URL
    FIWARE_ORION_BASE_URL = "http://localhost:1026/v2/entities/"

    try:
        # Query Orion to get all entities of type Photo with the specified vine_id
        fiware_orion_url = f"{FIWARE_ORION_BASE_URL}?type={entity_type}&q=vine_id=={vine_id}"

        photo_response = requests.get(fiware_orion_url)

        if photo_response.status_code == 200:
            photo_data = photo_response.json()
            photo_url = [entity['photo']['value'] for entity in photo_data if 'photo' in entity]
            return photo_url
        else:
            print(f"Failed to retrieve vine data. Status code: {photo_response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


vine_row_id = "vinerow001"

# Find all vines in vinerow X
vine_data_vinerow = find_vines_in_vinerow("Vine", vine_row_id)

if vine_data_vinerow is not None:
    # Find all photo URLs associated with the vines in vinerow
    print("Photo URLs associated with vines in " + vine_row_id + ":")

    for vine_id in vine_data_vinerow:
        photos_vinerow = find_photos_for_vines("Photo", vine_id)

        if photos_vinerow is not None:

            for photo_url in photos_vinerow:
                print("Vine ID: " + vine_id + " Photo URL: " + photo_url)
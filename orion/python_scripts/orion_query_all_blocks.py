import requests

def get_all_blocks():
    # Orion Context Broker API base URL
    FIWARE_ORION_BASE_URL = "http://localhost:1026/v2/entities/"

    block_coordinates_list = []  # List to store block ID and coordinates

    try:
        # Query Orion to get all entities of type "Block"
        fiware_orion_url_block = f"{FIWARE_ORION_BASE_URL}?type=Block"
        block_response = requests.get(fiware_orion_url_block)

        if block_response.status_code == 200:
            block_data = block_response.json()
            for block_entity in block_data:
                block_id = block_entity['id']
                print(f"Block ID: {block_id}")

                # Extract coordinates
                coordinates = block_entity['geom']['value']['coordinates']
                block_coordinates_list.append((block_id, coordinates))

                # Print attributes of the block
                for attribute, value in block_entity.items():
                    if attribute != 'id' and attribute != 'type':
                        print(f"{attribute}: {value['value']}")
                print()  # Add a new line for better readability
        else:
            print(f"Failed to retrieve block data. Status code: {block_response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    return block_coordinates_list

# Example usage
block_coordinates_list = get_all_blocks()
for block_id, coordinates in block_coordinates_list:
    print(f"Block ID: {block_id}, Coordinates: {coordinates}")
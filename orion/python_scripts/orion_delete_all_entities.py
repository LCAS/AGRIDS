import requests

def delete_all_entities():
    # Define the Fiware Orion URL for querying all entities
    orion_url = "http://localhost:1026/v2/entities/"

    # Query all entities
    try:
        response = requests.get(orion_url)
        if response.status_code == 200:
            entities = response.json()
            for entity in entities:
                entity_id = entity["id"]
                delete_entity(entity_id)
            print("All entities deleted successfully.")
        else:
            print(f"Error querying entities. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error querying entities: {str(e)}")

def delete_entity(entity_id):
    # Define the Fiware Orion URL and entity ID
    orion_url = "http://localhost:1026/v2/entities/"
    entity_url = orion_url + entity_id

    # Use requests to send the DELETE request
    try:
        response = requests.delete(entity_url)
        if response.status_code == 204:
            print(f"Entity {entity_id} deleted successfully.")
        else:
            print(f"Error deleting entity {entity_id}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error deleting entity {entity_id}: {str(e)}")

# Call delete_all_entities function to delete all entities
delete_all_entities()

import subprocess

# Specify the entity ID you want to delete
entity_id_to_delete = "vine001"

def delete_entity(entity_id):
    # Define the Fiware Orion URL and entity ID
    orion_url = "http://localhost:1026/v2/entities/"
    entity_url = orion_url + entity_id

    # Use curl to send the DELETE request
    try:
        subprocess.run(["curl", "-X", "DELETE", entity_url], check=True)
        print(f"Entity {entity_id} deleted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error deleting entity {entity_id}. Status code: {e.returncode}")

# Call the delete_entity function with the specified entity ID
delete_entity(entity_id_to_delete)

import requests
import json

def create_vine_entity(base_url, key, vine_data):
    # Convert data to JSON
    vine_json = json.dumps(vine_data)

    # Headers for JSON content
    headers = {'Content-Type': 'application/json'}

    # Create Vine entity in Zenoh
    response = requests.put(f"{base_url}/{key}", data=vine_json, headers=headers)

    # Print response
    if response.status_code == 200:
        print(f"Entity {key} created successfully")
    else:
        print(f"Failed to create entity {key}. Status code: {response.status_code}")
        print("Response:", response.text)

# Example usage:
create_vine_entity(
    base_url="http://localhost:10000/demo/example",
    key="vine001",
    vine_data={
        "id": "vine001",
        "type": "Vine",
        "vine_row_id": {"value": "vinerow001", "type": "String"},
        "user_defined_id": {"value": "Vine 1", "type": "String"},
        "variety": {"value": "Merlot", "type": "String"},
        "clone": {"value": "Chardonnay", "type": "String"},
        "rootstock": {"value": "3309C", "type": "String"},
        "location": {"type": "geo:json", "value": {"type": "Point", "coordinates": [53.227216007632244, -0.5493656119079906]}},
        "grapes_number": {"value": 5, "type": "Integer"},
        "grapes_yield": {"value": 4.8, "type": "Float"}
    }
)

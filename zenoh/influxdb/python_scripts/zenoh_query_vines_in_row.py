# Doesn't Work

import requests

def query_keys(base_url, vine_row_id):
    url = f"{base_url}/vine"  # Get all keys
    response = requests.get(url)
    print(response.json())
    
    if response.status_code == 200:
        keys_data = response.json()
        keys_in_vine_row = []
        for key, value in keys_data.items():
            if value.get("vine_row_id", {}).get("value") == vine_row_id:
                keys_in_vine_row.append(key)
        print(f"Keys in vine_row_id {vine_row_id}: {keys_in_vine_row}")
    else:
        print(f"Failed to retrieve keys. Status code: {response.status_code}")

if __name__ == "__main__":
    base_url = "http://localhost:10000/demo/example"
    vine_row_id = "vinerow001"
    query_keys(base_url, vine_row_id)

import requests

def query_keys(base_url, key):
    url = f"{base_url}/{key}?_time=[..]"
    response = requests.get(url)
    
    if response.status_code == 200:
        keys = response.json()
        print(f"Data in {key}: {keys}")
    else:
        print(f"Failed to retrieve data in {key}. Status code: {response.status_code}")

if __name__ == "__main__":
    base_url = "http://localhost:10000/demo/example"
    key = "vine001"
    query_keys(base_url, key)

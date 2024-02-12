import requests

def delete_data(base_url, key):
    url = f"{base_url}/{key}?_time=[..]"
    response = requests.delete(url)
    
    if response.status_code == 204:
        print(f"Data associated with key '{key}' deleted successfully.")
    else:
        print(f"Failed to delete data associated with key '{key}'. Status code: {response.status_code}")

if __name__ == "__main__":
    base_url = "http://localhost:10000/demo/example"
    key = "test"
    delete_data(base_url, key)

# curl -X DELETE http://localhost:10000/demo/example/test?_time=[..]
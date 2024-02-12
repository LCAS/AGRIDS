import requests
import json

# URL endpoint
url = 'http://localhost:10000/s3/example/test'

# JSON data to be sent in the request body
data = {
    "example_key": "example_value"
}

# Headers
headers = {
    'content-type': 'application/json'
}

# Making the PUT request
response = requests.put(url, headers=headers, data=json.dumps(data))

# Checking response status
if response.status_code == 200:
    print("Request successful")
else:
    print("Request failed with status code:", response.status_code)

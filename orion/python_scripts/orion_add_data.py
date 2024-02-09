import requests
import json

url = "http://localhost:1026/v2/entities"
headers = {
    "Content-Type": "application/json"
}

data = {
    "id": "Room5",
    "type": "Room",
    "temperature": {
        "value": 19,
        "type": "Float"
    },
    "pressure": {
        "value": 700,
        "type": "Integer"
    }
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 201:
    print("Entity created successfully")
else:
    print("Failed to create entity. Status code:", response.status_code)
    print("Response:", response.text)

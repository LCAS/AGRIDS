import requests

url = 'http://localhost:1026/v2/subscriptions/'

headers = {
    'Content-Type': 'application/json',
    'fiware-service': 'openiot',
    'fiware-servicepath': '/'
}

data = {
    "description": "Notify Draco of all context changes",
    "subject": {
        "entities": [
            {
                "idPattern": ".*"
            }
        ]
    },
    "notification": {
        "http": {
            "url": "http://localhost:5050/v2/notify"
        }
    },
    "throttling": 5
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 201:
    print("Subscription created successfully.")
else:
    print(f"Failed to create subscription. Status code: {response.status_code}")
    print(response.text)

import requests
import json

orion_url = 'http://localhost:1026/v2/entities'
subscription_url = 'http://localhost:1026/v2/subscriptions'
notification_endpoint = 'http://cygnus:5051/notify' # cygnus

headers = {
    'Content-Type': 'application/json'
}

# Fetching the list of entities from Orion
response = requests.get(orion_url)
entities = response.json()

def create_subscription(entity_id, entity_type, attribute, endpoint):
    subscription_payload = {
        "description": f"Notify me of changes in {entity_id} - {attribute}",
        "subject": {
            "entities": [
                {
                    "id": entity_id,
                    "type": entity_type,
                    "fiware-service": "openiot"
                }
            ],
            "condition": {
                "attrs": [attribute],
                "notifyOnMetadataChange": True,  # Set to False to exclude metadata changes
            }
        },
        "notification": {
            "http": {
                "url": endpoint,
            },
        }
    }

    response = requests.post(subscription_url, headers=headers, data=json.dumps(subscription_payload))

    if response.status_code == 201:
        print(f"Subscription created successfully for {entity_id} - {attribute}")
    elif response.status_code == 409:
        print(f"Subscription already exists for {entity_id} - {attribute}")
    else:
        print(f"Failed to create subscription for {entity_id} - {attribute}. Status code: {response.status_code}")
        print(response.text)

for entity in entities:
    for attribute, attribute_value in entity.items():
        # Skip non-dictionary attributes (like "id" and "type")
        if not isinstance(attribute_value, dict):
            continue
        
        create_subscription(entity["id"], entity["type"], attribute, notification_endpoint)

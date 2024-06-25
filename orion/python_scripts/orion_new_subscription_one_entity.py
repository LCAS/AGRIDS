import requests
import json

subscription_url = "http://localhost:1026/v2/subscriptions"
notification_endpoint = "http://cygnus:5051/notify" # cygnus

headers = {
    "Content-Type": "application/json",
    "fiware-servicepath": "/",
    "fiware-service": "openiot"
}

def create_subscription(entity_id, entity_type, attribute, endpoint):
    subscription_payload = {
        "description": f"Notify me of changes in {entity_id} - {attribute}",
        "subject": {
            "entities": [
                {
                    "id": entity_id,
                    "type": entity_type
                }
            ],
            "condition": {
                "attrs": [attribute],
                "notifyOnMetadataChange": True  # Set to False to exclude metadata changes
            }
        },
        "notification": {
            "http": {
                "url": endpoint,
            },
            "onlyChangedAttrs": True  # Set to True to receive only changed attributes
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

# Example useage
entity_id = "vine003"
entity_type ="Vine"
attribute = "grapes_number"

create_subscription(entity_id, entity_type, attribute, notification_endpoint)

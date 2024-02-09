import requests
import json
import logging

ORION_URL = 'http://localhost:1026/v2/entities'
SUBSCRIPTION_URL = 'http://localhost:1026/v2/subscriptions'
NOTIFICATION_ENDPOINT = 'http://cygnus:5051/notify'  # Cygnus

HEADERS = {
    'Content-Type': 'application/json'
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_subscription(endpoint):
    subscription_payload = {
        "description": "Notify me of all changes",
        "subject": {
            "entities": [
                {
                    "idPattern": ".*",
                    "typePattern": ".*"
                }
            ],
            "condition": {
                "attrs": [],
                "expression": {}
            }
        },
        "notification": {
            "http": {
                "url": endpoint,
            },
        }
    }

    try:
        response = requests.post(SUBSCRIPTION_URL, headers=HEADERS, data=json.dumps(subscription_payload))
        response.raise_for_status()
        if response.status_code == 201:
            logger.info("Subscription created successfully for all changes")
        elif response.status_code == 409:
            logger.info("Subscription already exists for all changes")
        else:
            logger.error(f"Failed to create subscription for all changes. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to create subscription for all changes. Error: {e}")


def main():
    try:
        create_subscription(NOTIFICATION_ENDPOINT)
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to create subscription for all changes. Error: {e}")


if __name__ == "__main__":
    main()

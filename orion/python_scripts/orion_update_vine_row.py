import requests
import json

ORION_ENDPOINT_BASE = 'http://localhost:1026/v2/entities/'

# Vine entity ID
entity_id = '0827ece3-d0ba-4059-becf-5a227c90a9a1'

ORION_ENDPOINT = f'{ORION_ENDPOINT_BASE}{entity_id}/attrs' # may or may not need "/attrs" at the end

updated_data = {
    "user_defined_id": {
        "value": "fr8",
        "type": "String"
    }
}

# Convert updated data to JSON
updated_vine_json = json.dumps(updated_data)

# Headers for JSON content
headers = {'Content-Type': 'application/json'}

# Update Vine entity in Orion using PATCH request
response = requests.patch(ORION_ENDPOINT, data=updated_vine_json, headers=headers)

# Print response
if response.status_code == 204:
    print("Entity updated successfully")
else:
    print("Failed to update entity. Status code:", response.status_code)
    print("Response:", response.text)

# send notifcation
#notification_endpoint = 'http://localhost:5080/notify'

# Send POST request to the notification endpoint
#response = requests.post(notification_endpoint, data=updated_vine_json, headers=headers)

# Print response
#if response.status_code == 200:
#    print("Notification sent successfully")
#else:
#    print("Failed to send notification. Status code:", response.status_code)
#    print("Response:", response.text)

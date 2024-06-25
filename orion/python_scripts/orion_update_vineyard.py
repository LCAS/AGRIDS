import requests
import json

ORION_ENDPOINT_BASE = 'http://localhost:1026/v2/entities/'

# Vine entity ID
entity_id = 'ee18b6da-b385-4074-9323-923916b8b539'

ORION_ENDPOINT = f'{ORION_ENDPOINT_BASE}{entity_id}/attrs' # may or may not need "/attrs" at the end

geom_coordinates = [
          [
            -0.5247154066915182, 53.268215050892096
          ],
          [
            -0.5242304808970949, 53.26826105337497
          ],
          [
            -0.5241747844753734, 53.268002589147606
          ],
          [
            -0.5246320547124407, 53.2679710977553
          ],
          [
            -0.5247154066915182, 53.268215050892096
          ]
        ]

updated_data = {
    # "vineyard_id": {
    #    "value": "jojo",
    #    "type": "String"
    # },
    # "name": {
    #    "value": "JoJos Vineyard", 
    #    "type": "String"
    # },
    # "street_address": {
    #     "value": "Russells Water, Henley-on-Thames, RG9 6EU",
    #     "type": "String"
    # },
    # "owner": {
    #     "value": "Harrow and Hope Limited",
    #     "type": "String"
    # },
    "geom": {
        "type": "geo:json",
        "value": {
            "type": "MultiPoint",
            "coordinates": geom_coordinates
        }
    }
}

# Convert updated data to JSON
updated_data_json = json.dumps(updated_data)

# Headers for JSON content
headers = {'Content-Type': 'application/json'}

# Update Vine entity in Orion using PATCH request
response = requests.patch(ORION_ENDPOINT, data=updated_data_json, headers=headers)

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

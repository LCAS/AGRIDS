import requests

orion_url = 'http://localhost:1026/v2/subscriptions'

response = requests.get(orion_url)
subscriptions = response.json()

for subscription in subscriptions:
    print(f"Subscription ID: {subscription['id']}, Status: {subscription['status']}")

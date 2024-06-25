import requests

orion_url = 'http://localhost:1026/v2/subscriptions'

response = requests.get(orion_url)
subscriptions = response.json()
total = 0

for subscription in subscriptions:
    total += 1
    print(f"Subscription ID: {subscription['id']}, Status: {subscription['status']}")

print("Total subscriptions: " + str(total))

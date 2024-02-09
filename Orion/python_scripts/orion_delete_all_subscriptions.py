import requests

orion_url = 'http://localhost:1026/v2/subscriptions'

def delete_all_subscriptions():
    # Fetching the list of subscriptions from Orion
    response = requests.get(orion_url)
    subscriptions = response.json()

    for subscription in subscriptions:
        subscription_id = subscription.get('id')
        if subscription_id:
            delete_subscription(subscription_id)

def delete_subscription(subscription_id):
    delete_url = f'{orion_url}/{subscription_id}'
    response = requests.delete(delete_url)

    if response.status_code == 204:
        print(f"Subscription {subscription_id} deleted successfully.")
    else:
        print(f"Failed to delete subscription {subscription_id}. Status code: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    delete_all_subscriptions()

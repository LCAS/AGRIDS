import requests

# URL endpoint
url = 'http://0.0.0.0:10000/s3/example/vine001'

# Making the GET request
response = requests.get(url)

# Checking response status
if response.status_code == 200:
    # Print the response content in a readable format
    data = response.json()[0]['value']
    print("ID:", data['id'])
    print("Type:", data['type'])
    print("Vine Row ID:", data['vine_row_id']['value'])
    print("User Defined ID:", data['user_defined_id']['value'])
    print("Variety:", data['variety']['value'])
    print("Clone:", data['clone']['value'])
    print("Rootstock:", data['rootstock']['value'])
    print("Location (Latitude, Longitude):", data['location']['value']['coordinates'])
    print("Grapes Number:", data['grapes_number']['value'])
    print("Grapes Yield:", data['grapes_yield']['value'])
else:
    print("Request failed with status code:", response.status_code)

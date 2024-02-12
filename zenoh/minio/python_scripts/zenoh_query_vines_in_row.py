import requests

# URL endpoint for querying vine IDs in a vine row
base_url = 'http://0.0.0.0:10000/s3/example/'
vine_row_id = 'your_vine_row_id_here'
url = base_url + 'query_vine_ids?vine_row_id=' + vine_row_id

# Making the GET request
response = requests.get(url)

# Checking response status
if response.status_code == 200:
    # Print the vine IDs
    vine_ids = response.json()
    print("Vine IDs in Vine Row", vine_row_id, ":")
    for vine_id in vine_ids:
        print(vine_id)
else:
    print("Request failed with status code:", response.status_code)

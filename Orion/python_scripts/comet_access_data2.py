import requests

# Define FIWARE Comet endpoint URL
comet_url = "http://cabbage-xps-8900:8666/STH/v1/contextEntities/type/Vine/id/vine001/attributes/grapes_number?lastN=3"

# http://cabbage-xps-8900:8666/STH/v1/contextEntities/type/Vine/id/vine001/attributes/grapes_number?hLimit=3&hOffset=0&dateFrom=2024-02-01T00:00:00.000Z&dateTo=2024-02-01T23:59:59.999Z

# Define headers with content type JSON
headers = {
    "fiware-service": "openiot",
    "fiware-servicepath": "/"
}

# Make the GET request to retrieve all data
response = requests.get(f"{comet_url}", headers=headers)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the response JSON data
    data = response.json()
    
    print(data)
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")

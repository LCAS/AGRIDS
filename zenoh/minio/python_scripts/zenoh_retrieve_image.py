import requests
import base64
import json

def download_image_from_zenoh(url, output_filename):
    response = requests.get(url)    
    if response.status_code == 200:
        #data = response.json()[0]['value']

        decoded_data = base64.b64decode(response.content)

        print(decoded_data)

        # Decode the base64-encoded data
        #decoded_data = base64.b64decode(data)

        with open(output_filename, 'wb') as f:
            f.write(decoded_data)
        print(f"Image downloaded successfully as {output_filename}")
    else:
        print("Failed to download image")

# Example usage
zenoh_base_url = 'http://localhost:10000/s3/example/'
file_name = 'vine001.jpg'
zenoh_url = zenoh_base_url + file_name
output_filename = 'downloaded_image.jpg'
download_image_from_zenoh(zenoh_url, output_filename)

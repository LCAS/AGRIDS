# Dosent work

import requests

def upload_image(file_path_local, file_path_zenoh):
    # Headers
    headers = {
        'content-type': 'application/json'
    }
    
    url = 'http://localhost:10000/s3/example/' + file_path_zenoh
    files = {'file': open(file_path_local, 'rb')}

    response = requests.put(url, headers=headers, data=files)

    if response.status_code == 200:
        print("Image uploaded successfully")
    else:
        print("Failed to upload image")

# Example usage
file_path_local = 'vine001.jpg' # path to file and file name on local drive
file_path_zenoh = 'vine001.jpg' # path to file and file name stroed in zenoh and minio
upload_image(file_path_local, file_path_zenoh)
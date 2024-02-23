from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import json

def store_photo_data(photo_id, vine_id, vinerow_id, block_id, vineyard_id, file_name):
    # InfluxDB credentials
    url = "http://localhost:8086"
    token = "Yk4TdmYvo95inSvUT4ohlm3NPcSJ0nfvzBPwANtBEs2nu28fGjXauu4vs_zbvB7TedF1PqJYZzOvLTlzCz-GbA=="
    org = "7829dda3fdb40c4a"
    bucket = "vineyard001"
    
    # InfluxDB client
    influx_client = InfluxDBClient(url=url, token=token, org=org)
    
    # Create InfluxDB write client
    write_api = influx_client.write_api(write_options=SYNCHRONOUS)

    # Constructing the photo URL
    photo_url = f"{vineyard_id}/{block_id}/{vinerow_id}/{vine_id}/{file_name}"    

    # Create InfluxDB point for photo data
    point = Point(photo_id) \
        .tag("photo_id", photo_id) \
        .tag("vine_id", vine_id) \
        .field("photo_url", photo_url)
    
    # Write vine data to InfluxDB and get feedback
    try:
        write_api.write(bucket=bucket, org=org, record=point)
        print("Photo data " + photo_id + " stored successfully in InfluxDB")
    except Exception as e:
        print("Error storing photo data in InfluxDB:", e)
    
    # Close the InfluxDB client
    influx_client.close()

# Example usage:
photo_id="photo001"
vine_id="vine001"
vineyard_id="vineyard001"
block_id="block001"
vinerow_id="vinerow001"
file_name="photo001.jpg"

store_photo_data(photo_id, vine_id, vinerow_id, block_id, vineyard_id, file_name)

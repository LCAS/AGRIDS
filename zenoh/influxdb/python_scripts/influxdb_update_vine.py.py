from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import json

def update_grapes_number(vine_id, new_grapes_number):
    # InfluxDB credentials
    url = "http://localhost:8086"
    token = "Yk4TdmYvo95inSvUT4ohlm3NPcSJ0nfvzBPwANtBEs2nu28fGjXauu4vs_zbvB7TedF1PqJYZzOvLTlzCz-GbA=="
    org = "7829dda3fdb40c4a"
    bucket = "vineyard001"
    
    # InfluxDB client
    influx_client = InfluxDBClient(url=url, token=token, org=org)
    
    # Create InfluxDB write client
    write_api = influx_client.write_api(write_options=SYNCHRONOUS)
    
    # Query the existing grapes_number value
    query = f'from(bucket: "{bucket}") \
        |> range(start: -1m) \
        |> filter(fn: (r) => r["_measurement"] == "{vine_id}") \
        |> filter(fn: (r) => r["_field"] == "grapes_number") \
        |> last()'
    result = influx_client.query_api().query(org=org, query=query)
    
    # Create InfluxDB point for updating grapes_number
    point = Point(vine_id) \
        .field("grapes_number", new_grapes_number)
    
    # Write the updated grapes_number to InfluxDB
    write_api.write(bucket=bucket, org=org, record=point)
    print(f"Grapes number for vine {vine_id} updated successfully to {new_grapes_number}")

    # Close the InfluxDB client
    influx_client.close()

# Example vine data
vine_id = "vine001"
new_grapes_number = 25

update_grapes_number(vine_id, new_grapes_number)

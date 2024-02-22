from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import json

def store_block_data(block_id, user_defined_id, street_address, row_spacing_m, vine_spacing_m, date_start, date_end, geom_coordinates):
    # InfluxDB credentials
    url = "http://localhost:8086"
    token = "Yk4TdmYvo95inSvUT4ohlm3NPcSJ0nfvzBPwANtBEs2nu28fGjXauu4vs_zbvB7TedF1PqJYZzOvLTlzCz-GbA=="
    org = "7829dda3fdb40c4a"
    bucket = "vineyard"
    
    # InfluxDB client
    influx_client = InfluxDBClient(url=url, token=token, org=org)
    
    # Create InfluxDB write client
    write_api = influx_client.write_api(write_options=SYNCHRONOUS)
    
    # Create InfluxDB point for block data
    point = Point(block_id) \
        .tag("user_defined_id", user_defined_id) \
        .tag("street_address", street_address) \
        .tag("row_spacing_m", row_spacing_m) \
        .tag("vine_spacing_m", vine_spacing_m) \
        .tag("date_start", date_start) \
        .tag("date_end", date_end) \
        .tag("geom", json.dumps(geom_coordinates))
    
    # Write block data to InfluxDB and get feedback
    try:
        write_api.write(bucket=bucket, org=org, record=point)
        print("Block data stored successfully in InfluxDB")
    except Exception as e:
        print("Error storing block data in InfluxDB:", e)
    
    # Close the InfluxDB client
    influx_client.close()

# Example block data
block_id = "block001"
user_defined_id = "North Block"
street_address = "123 Vine Street"
row_spacing_m = 1.5
vine_spacing_m = 1.0
date_start = "2024-01-01T00:00:00Z"
date_end = "2024-12-31T00:00:00Z"
geom_coordinates = [
    [53.227176516724036, -0.5490537449585962],
    [53.22715082571518, -0.5489410921784628],
    [53.22712754322504, -0.5491033658260358],
    [53.227084189589014, -0.5489384099694119]
]

store_block_data(block_id, user_defined_id, street_address, row_spacing_m, vine_spacing_m, date_start, date_end, geom_coordinates)

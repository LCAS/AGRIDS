from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import json

def store_vine_row_data(vine_row_id, block_id, user_defined_id, orientation, geom_coordinates):
    # InfluxDB credentials
    url = "http://localhost:8086"
    token = "Yk4TdmYvo95inSvUT4ohlm3NPcSJ0nfvzBPwANtBEs2nu28fGjXauu4vs_zbvB7TedF1PqJYZzOvLTlzCz-GbA=="
    org = "7829dda3fdb40c4a"
    bucket = "vineyard001"
    
    # InfluxDB client
    influx_client = InfluxDBClient(url=url, token=token, org=org)
    
    # Create InfluxDB write client
    write_api = influx_client.write_api(write_options=SYNCHRONOUS)
    
    # Create InfluxDB point
    point = Point(vine_row_id) \
        .tag("block_id", block_id) \
        .field("user_defined_id", user_defined_id) \
        .tag("orientation", orientation) \
        .tag("geom_coordinates", json.dumps(geom_coordinates))
    
    # Write data to InfluxDB and get feedback
    try:
        write_api.write(bucket=bucket, org=org, record=point)
        print("Vine row data " + vine_row_id + " stored successfully in InfluxDB")
    except Exception as e:
        print("Error storing data in InfluxDB:", e)
    
    # Close the InfluxDB client
    influx_client.close()

# Example data
vine_row_id = "vinerow001"
block_id = "block001"
user_defined_id = "Vine Row 1"
orientation = 45
geom_coordinates = [
    [[53.227176516724036, -0.5490537449585962], [53.22716326979953, -0.5488767191612437]],
    [[53.22715082571518, -0.5489410921784628], [53.22712834606973, -0.5489840075232755]],
    [[53.22712754322504, -0.5491033658260358], [53.22705608998665, -0.548782841844466]]
]

store_vine_row_data(vine_row_id, block_id, user_defined_id, orientation, geom_coordinates)

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import json

def store_vine_data(vine_id, vine_row_id, user_defined_id, variety, clone, rootstock, geom_coordinates, grapes_number, grapes_yield):
    # InfluxDB credentials
    url = "http://localhost:8086"
    token = "Yk4TdmYvo95inSvUT4ohlm3NPcSJ0nfvzBPwANtBEs2nu28fGjXauu4vs_zbvB7TedF1PqJYZzOvLTlzCz-GbA=="
    org = "7829dda3fdb40c4a"
    bucket = "vineyard"
    
    # InfluxDB client
    influx_client = InfluxDBClient(url=url, token=token, org=org)
    
    # Create InfluxDB write client
    write_api = influx_client.write_api(write_options=SYNCHRONOUS)
    
    # Create InfluxDB point for vine data
    point = Point(vine_id) \
        .tag("vine_row_id", vine_row_id) \
        .tag("user_defined_id", user_defined_id) \
        .tag("variety", variety) \
        .tag("clone", clone) \
        .tag("rootstock", rootstock) \
        .tag("geom_coordinates", json.dumps(geom_coordinates)) \
        .field("grapes_number", grapes_number) \
        .field("grapes_yield", grapes_yield)
    
    # Write vine data to InfluxDB and get feedback
    try:
        write_api.write(bucket=bucket, org=org, record=point)
        print("Vine data stored successfully in InfluxDB")
    except Exception as e:
        print("Error storing vine data in InfluxDB:", e)
    
    # Close the InfluxDB client
    influx_client.close()

# Example vine data
vine_id = "vine006"
vine_row_id = "vinerow001"
user_defined_id = "Vine 6"
variety = "Merlot"
clone = "Chardonnay"
rootstock = "3309C"
geom_coordinates = [53.227216007632244, -0.5493656119079906]
grapes_number = 5
grapes_yield = 4.8

store_vine_data(vine_id, vine_row_id, user_defined_id, variety, clone, rootstock, geom_coordinates, grapes_number, grapes_yield)

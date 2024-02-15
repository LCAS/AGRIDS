from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import json
import zenoh
import time

# InfluxDB credentials
url = "http://localhost:8086"
token = "Yk4TdmYvo95inSvUT4ohlm3NPcSJ0nfvzBPwANtBEs2nu28fGjXauu4vs_zbvB7TedF1PqJYZzOvLTlzCz-GbA=="
org = "7829dda3fdb40c4a"
bucket = "vineyard"

# InfluxDB client
influx_client = InfluxDBClient(url=url, token=token, org=org)

# Create the bucket if it doesn't exist
if influx_client.buckets_api().find_bucket_by_name(bucket) is None:
    bucket = influx_client.buckets_api().create_bucket(bucket_name=bucket, retention_rules=None, org_id=org)

# InfluxDB write client
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

# Transform JSON data into InfluxDB format
def transform_data(data):
    vine_data = json.loads(data)
    vine_id = vine_data['id']
    vine_row_id = vine_data['vine_row_id']['value']
    user_defined_id = vine_data['user_defined_id']['value']
    variety = vine_data['variety']['value']
    clone = vine_data['clone']['value']
    rootstock = vine_data['rootstock']['value']
    grapes_number = vine_data['grapes_number']['value']
    grapes_yield = vine_data['grapes_yield']['value']
    
    # Create InfluxDB point
    point = Point(vine_id) \
        .tag("vine_row_id", vine_row_id) \
        .tag("user_defined_id", user_defined_id) \
        .tag("variety", variety) \
        .tag("clone", clone) \
        .tag("rootstock", rootstock) \
        .field("grapes_number", grapes_number) \
        .field("grapes_yield", grapes_yield)
    
    return point

def listener_callback(data):
    data_decode = data.payload.decode('utf-8')
    print(f"Received {data.kind} ('{data.key_expr}': '{data_decode}')")

    point = transform_data(data_decode)
    
    # Write data to InfluxDB
    write_api.write(bucket=bucket, org=org, record=point)

    print(f"Stored in InfuxDB Database: {bucket}. Data: {point}")   

if __name__ == "__main__":
    zn_session = zenoh.open()
    zn_sub = zn_session.declare_subscriber('vista/data', listener_callback)
    time.sleep(60)
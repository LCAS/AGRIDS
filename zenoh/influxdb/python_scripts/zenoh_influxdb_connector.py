from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import json
import zenoh
import time
import re

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

# Define patterns
patterns = {
    'vineyard': 'vineyard',
    'block': 'block',
    'vinerow': 'vinerow',
    'vine': 'vine',
    'photo': 'photo'
}

# Function to data determine type
def determine_type(id_str):
    for pattern, type_ in patterns.items():
        if re.match(f'^{pattern}\d+$', id_str):
            return type_
    return None

# Transform JSON data into InfluxDB format
def transform_data(data):
    vineyard_data = json.loads(data)

    id_type = determine_type(vineyard_data['id'])

    if id_type == "vineyard":
        vineyard_id = vineyard_data['id']
        name = vineyard_data['vineyard_name']['value']
        street_address = vineyard_data['street_address']['value']
        owner = vineyard_data['owner']['value']
        geom = vineyard_data['geom']['value']
        
        # Create InfluxDB point
        point = Point(vineyard_id) \
            .tag("name", name) \
            .tag("street_address", street_address) \
            .tag("owner", owner) \
            .tag("geom", geom)
        
        return point
    
    elif id_type == "block":
        block_id = vineyard_data['id']
        vineyard_id = vineyard_data['vineyard_id']['value']
        user_defined_id = vineyard_data['user_defined_id']['value']
        row_spacing_m = vineyard_data['row_spacing_m']['value']
        vine_spacing_m = vineyard_data['vine_spacing_m']['value']
        date_start = vineyard_data['date_start']['value']
        date_end = vineyard_data['date_end']['value']
        geom = vineyard_data['geom']['value']
        
        # Create InfluxDB point
        point = Point(block_id) \
            .tag("user_defined_id", user_defined_id) \
            .tag("street_address", street_address) \
            .tag("row_spacing_m", row_spacing_m) \
            .tag("vine_spacing_m", vine_spacing_m) \
            .tag("date_start", date_start) \
            .tag("date_end", date_end) \
            .tag("geom", geom)
        
        return point  

    elif id_type == "vinerow":
        vine_row_id = vineyard_data['id']
        block_id = vineyard_data['block_id']['value']
        user_defined_id = vineyard_data['user_defined_id']['value']
        orientation = vineyard_data['orientation']['value']
        #geom = vineyard_data['geom']['value']
        
        # Create InfluxDB point
        point = Point(vine_row_id) \
            .tag("block_id", block_id) \
            .tag("user_defined_id", user_defined_id) \
            .tag("orientation", orientation)
        
        print("hello")
        print(vine_row_id)
        print(block_id)
        print(user_defined_id)
        print(orientation)
        print(point)
        
        return point

    elif id_type == "vine":
        vine_id = vineyard_data['id']
        vine_row_id = vineyard_data['vine_row_id']['value']
        user_defined_id = vineyard_data['user_defined_id']['value']
        variety = vineyard_data['variety']['value']
        clone = vineyard_data['clone']['value']
        #geom = vineyard_data['geom']['value']
        rootstock = vineyard_data['rootstock']['value']
        grapes_number = vineyard_data['grapes_number']['value']
        grapes_yield = vineyard_data['grapes_yield']['value']
        
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
    
    elif id_type == "photo":
        photo_id = vineyard_data['id']
        vine_id = vineyard_data['vine_id']['value']
        photo_url = vineyard_data['photo']['value']
        
        # Create InfluxDB point
        point = Point(photo_id) \
            .tag("vine_id", vine_id) \
            .tag("user_defined_id", user_defined_id) \
            .tag("photo", photo_url)
        
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
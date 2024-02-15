# Doesn't Work

# using influxdb v2
# pip install influxdb-client-python

from influxdb_client import InfluxDBClient
import json

# InfluxDB credentials
url = "http://localhost:8086"
token = "Yk4TdmYvo95inSvUT4ohlm3NPcSJ0nfvzBPwANtBEs2nu28fGjXauu4vs_zbvB7TedF1PqJYZzOvLTlzCz-GbA=="
org = "7829dda3fdb40c4a"
bucket = "zenoh_example"

def query_all_keys(bucket):
    client = InfluxDBClient(url=url, token=token, org=org)
    query = f'import "influxdata/influxdb/schema" schema.measurements(bucket: "{bucket}")'
    tables = client.query_api().query(query, org=org)    
    keys = set()
    for table in tables:
        for row in table:
            keys.add(row.values["_value"])

    return keys

def query_keys_in_row(bucket, vine_id):
    client = InfluxDBClient(url=url, token=token, org=org)

    query = 'from(bucket: "' + bucket + '")' \
            '|> range(start: -100h)' \
            '|> filter(fn: (r) => r["_measurement"] == "' + vine_id + '")' \
            '|> filter(fn: (r) => r["_field"] == "value")' \
            '|> yield(name: "last")'

    tables = client.query_api().query(query, org=org)

    for table in tables:
        for record in table.records:
            return record.values["_value"]
            #print(record.values["_value"])
        
def get_vine_ids_in_vine_row(vine_ids, bucket, vine_row_id):
    matching_vine_ids = set()

    for vine_id in vine_ids:
        json_data = query_keys_in_row(bucket, vine_id)

        for item in json_data:
            vine_row_id_value = item.get("vine_row_id", {}).get("value")
            print(vine_row_id_value)
            
            if vine_row_id_value == vine_row_id:
                matching_vine_ids.add(vine_id) # Add vine id to list of vines in row X

    return matching_vine_ids

if __name__ == "__main__":
    # Query all keys
    all_vine_id = query_all_keys(bucket)
    print("All keys:")
    print(all_vine_id)
    
    vine_row_id = "vinerow001"

    # Get vine IDs in target vine row
    matching_vine_ids = get_vine_ids_in_vine_row(all_vine_id, bucket, vine_row_id)

    # Print matching vine IDs
    #print(f"Vine IDs in {vine_row_id}:")
    #for vine_id in matching_vine_ids:
    #    print(vine_id)
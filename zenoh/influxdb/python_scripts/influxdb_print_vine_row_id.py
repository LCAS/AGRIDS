from influxdb_client import InfluxDBClient
import json

# InfluxDB credentials
url = "http://localhost:8086" 
token = "Yk4TdmYvo95inSvUT4ohlm3NPcSJ0nfvzBPwANtBEs2nu28fGjXauu4vs_zbvB7TedF1PqJYZzOvLTlzCz-GbA=="
org = "7829dda3fdb40c4a"
bucket = "zenoh_example"

def query_json_data(vine_id, bucket):
    client = InfluxDBClient(url=url, token=token, org=org)

    query = 'from(bucket: "' + bucket + '")' \
            '|> range(start: -10h)' \
            '|> filter(fn: (r) => r["_measurement"] == "' + vine_id + '")' \
            '|> filter(fn: (r) => r["_field"] == "value")' \
            '|> yield(name: "last")'

    tables = client.query_api().query(query, org=org)

    for table in tables:
        for record in table.records:
            return json.loads(record.values["_value"])

if __name__ == "__main__":
    vine_id = "vine001"

    # Query
    json_data = query_json_data(vine_id, bucket)

    # Extract vine_row_id from JSON data
    if json_data:
        vine_row_id = json_data.get("vine_row_id", {}).get("value")
        print(f"vine_row_id for {vine_id}: {vine_row_id}")
    else:
        print(f"No data found for {vine_id}")

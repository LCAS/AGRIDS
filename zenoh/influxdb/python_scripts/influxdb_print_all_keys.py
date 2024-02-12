# using influxdb v2
# pip install influxdb-client-python

from influxdb_client import InfluxDBClient

# Set InfluxDB credentials
url = "http://localhost:8086" 
token = "Yk4TdmYvo95inSvUT4ohlm3NPcSJ0nfvzBPwANtBEs2nu28fGjXauu4vs_zbvB7TedF1PqJYZzOvLTlzCz-GbA=="
org = "7829dda3fdb40c4a"
bucket = "zenoh_example"

def print_measurements(bucket):
    client = InfluxDBClient(url=url, token=token, org=org)
    query = f'import "influxdata/influxdb/schema" schema.measurements(bucket: "{bucket}")'
    tables = client.query_api().query(query, org=org)
    for table in tables:
        for row in table:
            print(row["_value"])

if __name__ == "__main__":
    print("Measurements in bucket 'zenoh_examples':")
    print_measurements(bucket)
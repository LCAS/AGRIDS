from influxdb_client import InfluxDBClient, Point, WriteOptions

# InfluxDB credentials
url = "http://localhost:8086"
token = "Yk4TdmYvo95inSvUT4ohlm3NPcSJ0nfvzBPwANtBEs2nu28fGjXauu4vs_zbvB7TedF1PqJYZzOvLTlzCz-GbA=="
org = "7829dda3fdb40c4a"
bucket = "vineyard"

# Create client
client = InfluxDBClient(url=url, token=token, org=org)

# Delete data from bucket
delete_api = client.delete_api()

# Delete all data from the bucket
start = "1970-01-01T00:00:00Z"  # Start time for deletion (Unix epoch)
stop = "now()"  # End time for deletion (current time)
predicate = '_measurement="vine_row"'
delete_api.delete(start=start, stop=stop, bucket=bucket, predicate=predicate)

print("All data deleted from the bucket:", bucket)

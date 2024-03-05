from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# InfluxDB settings
url = "http://localhost:8086"
token = "Yk4TdmYvo95inSvUT4ohlm3NPcSJ0nfvzBPwANtBEs2nu28fGjXauu4vs_zbvB7TedF1PqJYZzOvLTlzCz-GbA=="
org = "7829dda3fdb40c4a"
bucket = "vineyard001"

# Initialize the InfluxDB client
client = InfluxDBClient(url=url, token=token)

# Get the query client
query_api = client.query_api()

# Define the delete query
delete_query = f'from(bucket: "{bucket}") |> range(start: -30d) |> filter(fn: (r) => r._measurement == "vine001") |> drop(columns: ["_start", "_stop", "_time", "_value"])'

# Execute the delete query
result = query_api.query(delete_query, org=org)

print(result)

# Close the client
client.__del__()

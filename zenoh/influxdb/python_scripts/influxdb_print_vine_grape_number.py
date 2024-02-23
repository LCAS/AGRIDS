from influxdb_client import InfluxDBClient

# InfluxDB credentials
url = "http://localhost:8086"
token = "Yk4TdmYvo95inSvUT4ohlm3NPcSJ0nfvzBPwANtBEs2nu28fGjXauu4vs_zbvB7TedF1PqJYZzOvLTlzCz-GbA=="
org = "7829dda3fdb40c4a"
bucket = "vineyard001"
vine_id_to_query = "vine001"

# InfluxDB client
client = InfluxDBClient(url=url, token=token, org=org)

query = f'''
    from(bucket: "{bucket}")
        |> range(start: 0)
        |> filter(fn: (r) => r["_measurement"] == "{vine_id_to_query}")
        |> filter(fn: (r) => r["_field"] == "grapes_number")
        |> limit(n: 10)
'''

# Execute query
tables = client.query_api().query(query, org=org)

# Initialize a list to store the last 10 grapes_number values with timestamps
last_10_grapes_numbers = []

# Process query results
for table in tables:
    for row in table.records:
        grapes_number = row.values.get("_value")
        timestamp = row.values.get("_time")
        last_10_grapes_numbers.append((timestamp, grapes_number))

# Print the last 10 grapes_number values with timestamps
print(f"Last 10 Grapes Number with Timestamps for Vine ID {vine_id_to_query}:")
for i, (timestamp, grapes_number) in enumerate(last_10_grapes_numbers, 1):
    print(f"Value {i}: Grapes Number: {grapes_number}, Timestamp: {timestamp}")

# Close the InfluxDB client
client.close()

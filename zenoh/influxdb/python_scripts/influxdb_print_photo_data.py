from influxdb_client import InfluxDBClient

# InfluxDB credentials
url = "http://localhost:8086"
token = "Yk4TdmYvo95inSvUT4ohlm3NPcSJ0nfvzBPwANtBEs2nu28fGjXauu4vs_zbvB7TedF1PqJYZzOvLTlzCz-GbA=="
org = "7829dda3fdb40c4a"
bucket = "vineyard001"
vine_id_to_query = "vine001"

# InfluxDB client
client = InfluxDBClient(url=url, token=token, org=org)

# Construct InfluxDB query
query = f'''
    from(bucket: "{bucket}")
        |> range(start: 0)
        |> filter(fn: (r) => r["vine_id"] == "{vine_id_to_query}")    
        |> filter(fn: (r) => r["_field"] == "photo_url")    
        |> last()
'''

# Execute query
tables = client.query_api().query(query, org=org)

# Process query results
for table in tables:
    for row in table.records:
        photo_id = row.values.get("photo_id")
        vine_id = row.values.get("vine_id")
        photo_url = row.values.get("_value")

# Print the latest record
print(f"Photo ID: {photo_id}")
print(f"Vine ID: {vine_id}")
print(f"Photo URL: {photo_url}")

# Close the InfluxDB client
client.close()

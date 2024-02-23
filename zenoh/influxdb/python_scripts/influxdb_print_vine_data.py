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
        |> last()
'''

# Execute query
tables = client.query_api().query(query, org=org)

# Initialize variables to store the latest record
latest_record = {
    "vine_id": None,
    "vine_row_id": None,
    "user_defined_id": None,
    "variety": None,
    "clone": None,
    "rootstock": None,
    "geom_coordinates": None,
    "grapes_number": None,
    "grapes_yield": None
}

# Process query results
for table in tables:
    for row in table.records:
        vine_row_id = row.values.get("vine_row_id")
        user_defined_id = row.values.get("user_defined_id")
        variety = row.values.get("variety")
        clone = row.values.get("clone")
        rootstock = row.values.get("rootstock")
        geom_coordinates = row.values.get("geom_coordinates")
        grapes_number = row.values.get("_value") if row.values.get("_field") == "grapes_number" else None
        grapes_yield = row.values.get("_value") if row.values.get("_field") == "grapes_yield" else None

        # Update the latest record if the current record is newer
        if vine_row_id and user_defined_id and variety and clone and rootstock:
            latest_record["vine_row_id"] = vine_row_id
            latest_record["user_defined_id"] = user_defined_id
            latest_record["variety"] = variety
            latest_record["clone"] = clone
            latest_record["rootstock"] = rootstock
            latest_record["geom_coordinates"] = geom_coordinates
        if grapes_number is not None:
            latest_record["grapes_number"] = grapes_number
        if grapes_yield is not None:
            latest_record["grapes_yield"] = grapes_yield

# Print the latest record
print(f"Vine ID: {vine_id_to_query}")
print(f"Vine Row ID: {latest_record['vine_row_id']}")
print(f"User Defined ID: {latest_record['user_defined_id']}")
print(f"Variety: {latest_record['variety']}")
print(f"Clone: {latest_record['clone']}")
print(f"Rootstock: {latest_record['rootstock']}")
print(f"geom_coordinates: {latest_record['geom_coordinates']}")
print(f"Grapes Number: {latest_record['grapes_number']}")
print(f"Grapes Yield: {latest_record['grapes_yield']}")

# Close the InfluxDB client
client.close()

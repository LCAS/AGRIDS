from influxdb_client import InfluxDBClient

# InfluxDB credentials
url = "http://localhost:8086"
token = "Yk4TdmYvo95inSvUT4ohlm3NPcSJ0nfvzBPwANtBEs2nu28fGjXauu4vs_zbvB7TedF1PqJYZzOvLTlzCz-GbA=="
org = "7829dda3fdb40c4a"
bucket = "vineyard"

def query_vine_ids(vine_row_id):
    # Initialize client
    client = InfluxDBClient(url=url, token=token, org=org)

    # Construct Flux query
    query = f'''
        from(bucket:"{bucket}")
            |> range(start: 0)
            |> filter(fn: (r) => r["vine_row_id"] == "{vine_row_id}")
            |> group(columns: ["_measurement", "_field"])
            |> distinct(column: "_measurement")
    '''

    # Execute Flux query
    tables = client.query_api().query(query, org=org)

    # Extract vine IDs
    vine_ids = set()
    for table in tables:
        for record in table.records:
            vine_ids.add(record.get_value())

    return vine_ids

# Example usage
if __name__ == "__main__":
    vine_row_id = "vinerow001"
    vine_ids = query_vine_ids(vine_row_id)
    print("Vine IDs in " + str(vine_row_id) + ": " + str(vine_ids))
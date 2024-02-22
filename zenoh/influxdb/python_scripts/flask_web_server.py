from flask import Flask, render_template
from influxdb_client import InfluxDBClient

# Initialize Flask app
app = Flask(__name__)

# Function to query InfluxDB and retrieve the latest record
def query_influxdb_for_latest_record():
    # InfluxDB credentials
    url = "http://localhost:8086"
    token = "Yk4TdmYvo95inSvUT4ohlm3NPcSJ0nfvzBPwANtBEs2nu28fGjXauu4vs_zbvB7TedF1PqJYZzOvLTlzCz-GbA=="
    org = "7829dda3fdb40c4a"
    bucket = "vineyard"
    vine_id_to_query = "vine001"

    # InfluxDB client
    client = InfluxDBClient(url=url, token=token, org=org)

    # Construct InfluxDB query
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
        "vine_row_id": None,
        "user_defined_id": None,
        "variety": None,
        "clone": None,
        "rootstock": None,
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
            grapes_number = row.values.get("_value") if row.values.get("_field") == "grapes_number" else None
            grapes_yield = row.values.get("_value") if row.values.get("_field") == "grapes_yield" else None

            # Update the latest record if the current record is newer
            if vine_row_id and user_defined_id and variety and clone and rootstock:
                latest_record["vine_row_id"] = vine_row_id
                latest_record["user_defined_id"] = user_defined_id
                latest_record["variety"] = variety
                latest_record["clone"] = clone
                latest_record["rootstock"] = rootstock
            if grapes_number is not None:
                latest_record["grapes_number"] = grapes_number
            if grapes_yield is not None:
                latest_record["grapes_yield"] = grapes_yield

    # Close the InfluxDB client
    client.close()

    return latest_record

# Route for displaying the latest record
@app.route('/')
def display_latest_record():
    # Query InfluxDB for the latest record
    latest_record = query_influxdb_for_latest_record()

    vine_row_id = latest_record['vine_row_id']
    user_defined_id = latest_record['user_defined_id']
    variety = latest_record['variety']
    clone = latest_record['clone']
    rootstock = latest_record['rootstock']
    grapes_number = latest_record['grapes_number']
    grapes_yield = latest_record['grapes_yield']

    # Render the template with the latest record data
    return render_template('index.html',
                                        vine_id="None",
                                        bucket_name="None",
                                        vineyard_id="None",
                                        block_id="None",
                                        vine_row=vine_row_id,
                                        variety=variety,
                                        grapes_number=grapes_number,
                                        grapes_yield=grapes_yield,
                                        clone=clone,
                                        rootstock=rootstock,
                                        coordinates="None")

# Run the Flask app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)

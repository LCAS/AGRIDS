from flask import Flask, render_template, request
from influxdb_client import InfluxDBClient

import matplotlib.pyplot as plt
from datetime import datetime

from minio import Minio
from minio.error import S3Error

# Constants
MINIO_SERVER = "cabbage-xps-8900:9000"
MINIO_ACCESS_KEY = "KODXtyXxsNTbFrLEitSg"
MINIO_SECRET_KEY = "Ym3Cg3PHbjyIL35V6PEtp3ZQiNeIHeIYUgVC4cq0"
MINIO_SECURE = False

# Initialize Flask app
app = Flask(__name__)

def initialize_minio_client():
    return Minio(MINIO_SERVER, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=MINIO_SECURE)

# Function to query InfluxDB and retrieve the vine data record
def query_influxdb_for_latest_vine_data_record(url, token, org, bucket, vine_id_to_query):

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

    # Close the InfluxDB client
    client.close()

    return latest_record

# Function to query InfluxDB and retrieve the vine data record
def query_influxdb_for_latest_photo_data_record(url, token, org, bucket, vine_id_to_query):

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

    # Initialize variables to store the latest record
    latest_record = {
        "photo_id": None,
        "vine_id": None,
        "photo_url": None
    }

    # Process query results
    for table in tables:
        for row in table.records:
            latest_record["photo_id"] = row.values.get("photo_id")
            latest_record["vine_id"] = row.values.get("vine_id")
            latest_record["photo_url"] = row.values.get("_value")

    # Close the InfluxDB client
    client.close()

    return latest_record

# Function to query InfluxDB and retrieve the vine data for grape number over time
def query_influxdb_for_vine_data_grape_number_time(url, token, org, bucket, vine_id_to_query):

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

    # Initialize a list to store the last 10 grapes_number values
    last_10_grapes_numbers = []
    last_10_grapes_numbers_timestamps = []

    # Process query results
    for table in tables:
        for row in table.records:
            grapes_number = row.values.get("_value")
            timestamp = row.values.get("_time")
            last_10_grapes_numbers.append(grapes_number)
            last_10_grapes_numbers_timestamps.append(timestamp)

    # Close the InfluxDB client
    client.close()

    return last_10_grapes_numbers, last_10_grapes_numbers_timestamps

# Function to query InfluxDB and retrieve the vine data for grape number over time
def query_influxdb_for_block_id(url, token, org, bucket, vine_row_id_to_query):

    # InfluxDB client
    client = InfluxDBClient(url=url, token=token, org=org)

    query = f'''
        from(bucket: "{bucket}")
            |> range(start: 0)
            |> filter(fn: (r) => r["_measurement"] == "{vine_row_id_to_query}")
            |> last()
    '''

    # Execute query
    tables = client.query_api().query(query, org=org)

    block_id = None

    # Process query results
    for table in tables:
        for row in table.records:
            block_id = row.values.get("block_id")

    # Close the InfluxDB client
    client.close()

    return block_id

# Route for displaying the latest record
@app.route('/', methods=['GET', 'POST'])
def display_latest_record():
    vine_id_to_query = request.args.get('vine_id', 'vine001')  # Default to 'Vine_1' if not provided
    
    # InfluxDB credentials
    url = "http://localhost:8086"
    token = "Yk4TdmYvo95inSvUT4ohlm3NPcSJ0nfvzBPwANtBEs2nu28fGjXauu4vs_zbvB7TedF1PqJYZzOvLTlzCz-GbA=="
    org = "7829dda3fdb40c4a"
    bucket = "vineyard001"
    #vine_id_to_query = "vine001"

    # Query InfluxDB for the latest record
    latest_vine_data_record = query_influxdb_for_latest_vine_data_record(url, token, org, bucket, vine_id_to_query)
    latest_photo_data_record = query_influxdb_for_latest_photo_data_record(url, token, org, bucket, vine_id_to_query)
    grape_number_time_data, grape_number_time_data_timestamps = query_influxdb_for_vine_data_grape_number_time(url, token, org, bucket, vine_id_to_query)

    # Create a plot
    plt.figure(figsize=(10, 6))
    plt.plot(grape_number_time_data_timestamps, grape_number_time_data, marker='o')
    plt.title('Number of Grapes Over Time ' + vine_id_to_query)
    plt.xlabel('Timestamp')
    plt.ylabel('Number of Grapes')
    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability
    plt.tight_layout()

    # Save the plot to a PNG image
    grape_number_plot_path = 'static/plot.png'
    plt.savefig(grape_number_plot_path)

    vine_row_id = latest_vine_data_record['vine_row_id']
    user_defined_id = latest_vine_data_record['user_defined_id']
    variety = latest_vine_data_record['variety']
    clone = latest_vine_data_record['clone']
    rootstock = latest_vine_data_record['rootstock']
    geom_coordinates = latest_vine_data_record['geom_coordinates']
    grapes_number = latest_vine_data_record['grapes_number']
    grapes_yield = latest_vine_data_record['grapes_yield']
    photo_url = latest_photo_data_record['photo_url']

    # Get block id of vine query InfluxDB using vine row id from previous query
    block_id = query_influxdb_for_block_id(url, token, org, bucket, vine_row_id)
    
    minio_client = initialize_minio_client()

    # Split the path into two parts
    # File path is vineyard_name/block_name/vine_row_name/vine_name/FILE_PATH.jpg
    path_part = photo_url.split('/')
    BUCKET_NAME = path_part[0]
    FILE_PATH = path_part[1] + "/" + path_part[2] + "/" + path_part[3] + "/" + path_part[4]

    # Get the presigned URL for the image from MinIO the default expiry time is 7 days (604800 seconds)
    presigned_url = minio_client.presigned_get_object(BUCKET_NAME, FILE_PATH)

    # Render the template with the latest record data
    return render_template('index.html',
                                        vine_id=vine_id_to_query,
                                        bucket_name_minio=BUCKET_NAME,
                                        file_path=FILE_PATH,
                                        file_name = path_part[4],
                                        bucket_name_influx=bucket,
                                        vineyard_id=bucket,
                                        block_id=block_id,
                                        vine_row=vine_row_id,
                                        variety=variety,
                                        grapes_number=grapes_number,
                                        grapes_yield=grapes_yield,
                                        clone=clone,
                                        rootstock=rootstock,
                                        coordinates=geom_coordinates,
                                        image_url=presigned_url,
                                        grape_number_plot_path=grape_number_plot_path)

# Run the Flask app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)

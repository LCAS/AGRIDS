from flask import Flask, render_template, request, send_file, jsonify, json, make_response
from minio import Minio
from minio.error import S3Error
import requests

import mongodb_access_vine_data_last_values # Access historic data in MongoDB
import mongodb_access_multiple_vine_data_by_time # Access historic data in MongoDB
import matplotlib.pyplot as plt
from datetime import datetime
import time

from shapely.geometry import Point, LineString, Polygon
import numpy as np

import os

import orion_query_vines_in_block
import orion_query_vines_in_vine_row
import orion_add_block
import orion_add_vinerow
import orion_add_vine
import extend_line
import line_to_polygon as line_to_polygon
import export_to_geojson
import csv_upload_to_geojson
import interpolate_points
import vine_list_to_geojson
import export_to_antobot_xml
import export_geojson_to_antobot_xml
import export_to_pdf
import create_enclosing_polygons
import generate_topological_map
import mapbox_to_orion
import mapbox_to_orion_csv
import mapvit_to_orion
import orion_delete_entity
import geojson_to_orion
import export_to_topological_map
import export_to_kml
import topological_map_scripts.kml_to_tmap
import orion_add_vineyard
import get_padded_bounding_box
import csv_rows_vines_upload_to_geojson

from datetime import datetime
import ast

from pyproj import Geod

from geopy.distance import geodesic

import json
from io import BytesIO, StringIO

import re

import random

# Constants
MINIO_SERVER = os.getenv("MINIO_SERVER", "cabbage-xps-8900:9000") 
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "KODXtyXxsNTbFrLEitSg")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "Ym3Cg3PHbjyIL35V6PEtp3ZQiNeIHeIYUgVC4cq0")
MINIO_SECURE = os.getenv("MINIO_SECURE", False)

FIWARE_ORION_BASE_URL = os.getenv("FIWARE_ORION_BASE_URL", "http://cabbage-xps-8900:1026/v2/entities/")

app = Flask(__name__)

def initialize_minio_client():
    return Minio(MINIO_SERVER, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=MINIO_SECURE)

def get_fiware_entity_data(entity_id):
    fiware_orion_url = f"{FIWARE_ORION_BASE_URL}{entity_id}"
    response = requests.get(fiware_orion_url)
    if response.status_code == 200:
        fiware_data = response.json()
        return fiware_data
    else:
        return None
    
def get_fiware_data(entity_type_query, entity_type_id, entity_id):
    # Query Orion to get all entities of type "entity_type_query" of type "entity_type_id" with the specified "entity_id"
    fiware_orion_url = f"{FIWARE_ORION_BASE_URL}?type={entity_type_query}&q={entity_type_id}=={entity_id}"

    response = requests.get(fiware_orion_url)
    if response.status_code == 200:
        fiware_data = response.json()
        return fiware_data
    else:
        return None

# When drawing polygons check the coordinates are in order so the polygon dosen't overlap
def reorder_coordinates_clockwise(coordinates):
    # Convert lat-long coordinates to Point objects
    points = [Point(coord[1], coord[0]) for coord in coordinates]

    # Create a shapely Polygon from the points
    polygon = Polygon(points)

    # Get the centroid of the polygon
    centroid = polygon.centroid

    # Calculate the angles between each point and the centroid
    angles = np.arctan2(np.array([point.y - centroid.y for point in points]),
                        np.array([point.x - centroid.x for point in points]))

    # Sort the points based on their angles
    sorted_points = [point for _, point in sorted(zip(angles, points))]

    # Check the orientation of the polygon
    if polygon.area < 0:
        # If the area is negative, the polygon is clockwise, so reverse the order
        sorted_points = sorted_points[::-1]

    # Return the reordered lat-long coordinates
    reordered_coordinates = [[point.y, point.x] for point in sorted_points]
    
    return reordered_coordinates

def convert_to_unix_time_format(aggregated_results):
    converted_results = []
    for timestamp, total_grapes in aggregated_results.items():
        unix_time = int(time.mktime(datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').timetuple())) * 1000
        converted_results.append([unix_time, total_grapes])
    return converted_results

def calculate_polygon_area(coordinates):
    polygon = Polygon(coordinates)
    geod = Geod(ellps="WGS84")
    poly_area, poly_perimeter = geod.geometry_area_perimeter(polygon)
    return poly_area, poly_perimeter

# def calculate_line_length(coordinates):
#     geod = Geod('+a=6378137 +f=0.0033528106647475126')
    
#     # Check if coordinates are in the nested format
#     if isinstance(coordinates[0][0], list):
#         # Coordinates are in the nested format
#         flat_coordinates = [point for segment in coordinates for point in segment]
#     else:
#         # Coordinates are already flat
#         flat_coordinates = coordinates

#     # Extract latitudes and longitudes from the flattened coordinates list
#     lats = [coord[1] for coord in flat_coordinates]
#     lons = [coord[0] for coord in flat_coordinates]

#     total_length = geod.line_length(lons, lats)
#     return total_length

def calculate_line_length(coordinates):
    # Extract the first and last coordinates
    start_coord = coordinates[0]
    end_coord = coordinates[-1]

    # Calculate the total distance using geodesic
    total_distance = geodesic(start_coord, end_coord).meters

    return total_distance

def get_row_info(vine_row_data_list, block_id):
    total_rows = 0
    total_row_length = 0

    for row in vine_row_data_list:
        if row['block_id'] == block_id:
            total_rows += 1
            total_row_length = total_row_length + row['length']

    return total_rows, total_row_length
    
# Function to calculate midpoint between two coordinates
def calculate_midpoint(coord1, coord2):
    return [(coord1[0] + coord2[0]) / 2, (coord1[1] + coord2[1]) / 2]

@app.route('/', methods=['GET', 'POST'])
def index():

    try:
        return render_template('index.html'
                               )

    except Exception as exc:
        return f"Error: {exc}"

@app.route('/example', methods=['GET', 'POST'])
def example():
    
    block_data_list = []  # List to store block ID and coordinates
    vine_row_data_list = []  # List to store vine row ID and coordinates
    vine_data_list = []  # List to store vine ID and coordinates

    try:
        # Query Orion to get all entities of type "Block"
        fiware_orion_url_block = f"{FIWARE_ORION_BASE_URL}?type=Block&q=vineyard_id==vineyard001"
        block_response = requests.get(fiware_orion_url_block)

        if block_response.status_code == 200:
            block_data = block_response.json()
            for block_entity in block_data:
                block_id = block_entity['id']
                # Extract coordinates
                coordinates = block_entity['geom']['value']['coordinates']
                reordered_coordinates = reorder_coordinates_clockwise(coordinates)
                #block_data_list.append({'block_id': block_id, 'coordinates': reordered_coordinates})

                # Find all vine_ids and total number of vines given a block_id
                vine_data_list, total_vine_count, total_vine_row, vine_row_ids, total_grapes_count = orion_query_vines_in_block.find_vine_ids_in_block("Vine", "VineRow", block_id)
                block_data_list.append({'block_id': block_id, 'coordinates': reordered_coordinates, 'total_vine_count': total_vine_count, 'total_vine_row': total_vine_row, 'total_grapes_count': total_grapes_count})

        else:
            print(f"Failed to retrieve block data. Status code: {block_response.status_code}")

        # Query Orion to get all entities of type "VineRow"
        fiware_orion_url_vine_row = f"{FIWARE_ORION_BASE_URL}?type=VineRow&limit=200"
        vine_row_response = requests.get(fiware_orion_url_vine_row)

        if vine_row_response.status_code == 200:
            vinr_row_data = vine_row_response.json()
            for vine_row_entity in vinr_row_data:
                vine_row_id = vine_row_entity['id']
                # Extract coordinates
                coordinates = vine_row_entity['geom']['value']['coordinates']

                # Format coordinates
                #coordinates_formatted = []
                #for sublist in coordinates:
                #    for item in sublist:
                #        coordinates_formatted.append(item)

                # Find all vine_ids and total number of vines given a vine_row_id
                vine_ids, total_grapes_count, total_vine_count = orion_query_vines_in_vine_row.find_vine_ids_grapes_and_total_vines_in_row("Vine", vine_row_id)
                        
                vine_row_data_list.append({'vine_row_id': vine_row_id, 'coordinates': coordinates, 'total_grapes_count': total_grapes_count, 'total_vine_count': total_vine_count})
        else:
            print(f"Failed to retrieve vine_row data. Status code: {vine_row_response.status_code}")

        # Query Orion to get all entities of type "Vine"
        fiware_orion_url_vine = f"{FIWARE_ORION_BASE_URL}?type=Vine&limit=50"
        vine_response = requests.get(fiware_orion_url_vine)

        if vine_response.status_code == 200:
            vine_data = vine_response.json()
            for vine_entity in vine_data:
                vine_id = vine_entity['id']
                coordinates = vine_entity['location']['value']['coordinates']
                grapes_number = vine_entity['grapes_number']['value']

                vine_data_list.append({'vine_id': vine_id, 'coordinates': coordinates, 'grapes_number': grapes_number})
        else:
            print(f"Failed to retrieve vine data. Status code: {vine_response.status_code}")

        return render_template('example.html',
                                    block_data_list = block_data_list,
                                    vine_row_data_list = vine_row_data_list,
                                    vine_data_list = vine_data_list
                                    )

    except S3Error as exc:
        return f"Error: {exc}"

@app.route('/vine', methods=['GET', 'POST'])
def vine():
    minio_client = initialize_minio_client()
    entity_id = request.args.get('entity_id', 'vine001')  # Default to 'vine001' if not provided
    try:
        # Get data from Fiware Orion for a specific entity
        fiware_data = get_fiware_entity_data(entity_id)
        fiware_photo_data = get_fiware_data("Photo", "vine_id", entity_id)

        # TODO add error page
        if fiware_data is None:
            error_message = f"Entity with ID '{entity_id}' not found in Fiware Orion."
            #return render_template('index.html', error_message=error_message)

        # TODO add error page
        if fiware_photo_data is None:
            error_message = f"Photo with Vine ID '{entity_id}' not found in Fiware Orion."
            return render_template('vine.html', error_message=error_message)

        photo_url = [entity['photo']['value'] for entity in fiware_photo_data if 'photo' in entity][0] # Last is index number if vine ID has more than one photo

        # Extract BUCKET_NAME and FILE_PATH from photo_url
        if photo_url:
            # Split the path into two parts
            # File path is vineyard_name/block_name/vine_row_name/vine_name/FILE_PATH.jpg
            path_part = photo_url.split('/')
            BUCKET_NAME = path_part[0]
            FILE_PATH = path_part[1] + "/" + path_part[2] + "/" + path_part[3] + "/" + path_part[4]

            # Get the presigned URL for the image from MinIO the default expiry time is 7 days (604800 seconds)
            presigned_url = minio_client.presigned_get_object(BUCKET_NAME, FILE_PATH)
        
        else:
            return "photo_url not found in Fiware data"

        # Extract information from Fiware data
        #vineyard_id = fiware_data.get("vineyard_id", {}).get("value")
        #block_id = fiware_data.get("block_id", {}).get("value")
        vine_row = fiware_data.get("vine_row_id", {}).get("value")
        variety = fiware_data.get("variety", {}).get("value")
        grapes_number = fiware_data.get("grapes_number", {}).get("value")
        grapes_yield = fiware_data.get("grapes_yield", {}).get("value")
        clone = fiware_data.get("clone", {}).get("value")
        rootstock = fiware_data.get("rootstock", {}).get("value")
        coordinates = fiware_data.get("location", {}).get("value").get("coordinates")
        
        # Get the vine row data from Orion to get Block ID for vine
        fiware_vinerow_data = get_fiware_entity_data(vine_row)

        # TODO add error page
        if fiware_vinerow_data is None:
            error_message = f"Vine Row with ID '{vine_row}' not found in Fiware Orion."
            #return render_template('index.html', error_message=error_message)
    
        block_id = fiware_vinerow_data['block_id']['value']

        # Get the block data from Orion to get Vineyard ID for vine
        fiware_block_data = get_fiware_entity_data(block_id)

        # TODO add error page
        if fiware_vinerow_data is None:
            error_message = f"Block with ID '{block_id}' not found in Fiware Orion."
            #return render_template('index.html', error_message=error_message)
    
        vineyard_id = fiware_block_data['vineyard_id']['value']

        # Get historic data from MongoDB
        #mongodb_result = mongodb_access_vine_data_last_values.query_recent_values("vine001", "Vine", 10)
        mongodb_result = mongodb_access_vine_data_last_values.query_recent_values(entity_id, "Vine", 10)
        #grapes_number_list = [{result['recvTime'].strftime('%Y-%m-%d %H:%M:%S'), result['attrValue']} for result in mongodb_result]

        results_grape_number = []
        results_grape_number_timestamps = []
        grape_number_timestamp = zip(results_grape_number_timestamps, results_grape_number)

        for result in mongodb_result:
            results_grape_number.append(result.get('attrValue'))
            #results_grape_number_timestamps.append(result.get('recvTime'))
            results_grape_number_timestamps.append(int(time.mktime(result['recvTime'].timetuple())) * 1000) # converts to unix time,  * 1000 to convert to milliseconds

        grape_number_timestamp_data = [[timestamp, number] for timestamp, number in grape_number_timestamp]

        # Create a plot
        #plt.figure(figsize=(10, 6))
        #plt.plot(results_grape_number_timestamps, results_grape_number, marker='o')
        #plt.title('Number of Grapes Over Time ' + entity_id)
        #plt.xlabel('Timestamp')
        #plt.ylabel('Number of Grapes')
        #plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability
        #plt.tight_layout()

        # Save the plot to a PNG image
        #grape_number_plot_path = 'static/plot.png'
        #plt.savefig(grape_number_plot_path)
        
        return render_template('vine.html',
                                entity_id = entity_id,
                                bucket_name = BUCKET_NAME,
                                file_path = FILE_PATH,
                                file_name = path_part[4],
                                image_url = presigned_url,
                                vineyard_id = vineyard_id,
                                block_id = block_id,
                                vine_row = vine_row,
                                variety = variety,
                                grapes_number = grapes_number,
                                grape_number_timestamp_data = grape_number_timestamp_data,
                                #grape_number_plot_path = grape_number_plot_path,
                                grapes_yield = grapes_yield,
                                clone = clone,
                                rootstock = rootstock,
                                coordinates = coordinates)
    except S3Error as exc:
        return f"Error: {exc}"

@app.route('/vine_all', methods=['GET', 'POST'])
def vine_all():
    vine_coordinates_list = []  # List to store vine ID and coordinates

    try:
        # Query Orion to get all entities of type "Vine"
        fiware_orion_url_vine = f"{FIWARE_ORION_BASE_URL}?type=Vine&limit=50"
        vine_response = requests.get(fiware_orion_url_vine)

        if vine_response.status_code == 200:
            vine_data = vine_response.json()
            for vine_entity in vine_data:
                vine_id = vine_entity['id']
                # Extract coordinates
                coordinates = vine_entity['location']['value']['coordinates']

                vine_coordinates_list.append({'vine_id': vine_id, 'coordinates': coordinates})
        else:
            print(f"Failed to retrieve vine data. Status code: {vine_response.status_code}")
        

        return render_template('vine_all.html',
                                    vine_coordinates_list = vine_coordinates_list
                                    )

    except S3Error as exc:
        return f"Error: {exc}"
    
@app.route('/vine_add', methods=['GET', 'POST'])
def vine_add():

    try:
        vine_id = request.args.get('vine_id')

        respose_text = "None"
        
        if vine_id:
            # if vine_id is not empty
            
            user_defined_id = str(request.args.get('user_defined_id'))
            vine_row_id = str(request.args.get('vine_row_id'))
            variety = str(request.args.get('variety'))
            clone = str(request.args.get('clone'))
            rootstock = str(request.args.get('rootstock'))
            grapes_number = float(request.args.get('grapes_number'))
            grapes_yield = float(request.args.get('grapes_yield'))
            geom_coordinates_str = request.args.get('coordinates')
            geom_coordinates = ast.literal_eval(geom_coordinates_str)

            respose_text = orion_add_vine.create_vine_entity(str(vine_id), vine_row_id, user_defined_id, variety, clone, rootstock, geom_coordinates, grapes_number, grapes_yield)
            

        return render_template('vine_add.html',
                               respose_text = respose_text
                               )

    except S3Error as exc:
        return f"Error: {exc}"

@app.route('/block', methods=['GET', 'POST'])
def block():
    entity_id = request.args.get('entity_id', 'block001')  # Default to 'block001' if not provided

    try:
        # Get data from Fiware Orion for a specific entity
        fiware_data = get_fiware_entity_data(entity_id)

        # Extract information from Fiware data
        vineyard_id = fiware_data.get("vineyard_id", {}).get("value")
        user_defined_id = fiware_data.get("user_defined_id", {}).get("value")
        date_start = fiware_data.get("date_start", {}).get("value")
        date_end = fiware_data.get("date_end", {}).get("value")
        geom = fiware_data.get("geom", {}).get("value")
        coordinates = fiware_data.get("geom", {}).get("value", {}).get("coordinates", [])
        row_spacing_m = fiware_data.get("row_spacing_m", {}).get("value")
        vine_spacing_m = fiware_data.get("vine_spacing_m", {}).get("value")

        reordered_coordinates = reorder_coordinates_clockwise(coordinates)

        # Find all vine_ids and total number of vines given a block_id
        vine_data_list, total_vine_count, total_vine_row, vine_row_ids, total_grapes_count = orion_query_vines_in_block.find_vine_ids_in_block("Vine", "VineRow", entity_id)
        vine_ids = set()
        for vine, row in vine_data_list:
            vine_ids.add(vine)

        # find number of grapes over time given a list of vine ids
        aggregated_grape_number, earliest_timestamp = mongodb_access_multiple_vine_data_by_time.aggregate_grapes_over_time(vine_ids, 10)
        aggregated_grape_number = convert_to_unix_time_format(aggregated_grape_number)

        # TODO add error page
        if fiware_data is None:
            error_message = f"Entity with ID '{entity_id}' not found in Fiware Orion."
            #return render_template('index.html', error_message=error_message)

        return render_template('block.html',
                                    entity_id = entity_id,
                                    vineyard_id = vineyard_id,
                                    user_defined_id = user_defined_id,
                                    date_start = date_start,
                                    date_end = date_end,
                                    geom = geom,
                                    coordinates = reordered_coordinates,
                                    row_spacing_m = row_spacing_m,
                                    vine_spacing_m = vine_spacing_m,
                                    total_vine_count = total_vine_count,
                                    total_vine_row = total_vine_row,
                                    total_grapes_count = total_grapes_count,
                                    aggregated_grape_number = aggregated_grape_number
                                    )
    
    except S3Error as exc:
        return f"Error: {exc}"
    
@app.route('/block_all', methods=['GET', 'POST'])
def block_all():
    block_coordinates_list = []  # List to store block ID and coordinates

    try:
        # Query Orion to get all entities of type "Block"
        fiware_orion_url_block = f"{FIWARE_ORION_BASE_URL}?type=Block"
        block_response = requests.get(fiware_orion_url_block)

        if block_response.status_code == 200:
            block_data = block_response.json()
            for block_entity in block_data:
                block_id = block_entity['id']
                # Extract coordinates
                coordinates = block_entity['geom']['value']['coordinates']
                reordered_coordinates = reorder_coordinates_clockwise(coordinates)
                block_coordinates_list.append({'block_id': block_id, 'coordinates': reordered_coordinates})
        else:
            print(f"Failed to retrieve block data. Status code: {block_response.status_code}")
        

        return render_template('block_all.html',
                                    block_coordinates_list = block_coordinates_list
                                    )

    except S3Error as exc:
        return f"Error: {exc}"
    
@app.route('/block_add', methods=['GET', 'POST'])
def block_add():

    try:
        block_id = request.args.get('block_id')

        respose_text = "None"
        
        if block_id:
            # if block_id is not empty
            
            user_defined_id = str(request.args.get('user_defined_id'))
            vineyard_id = str(request.args.get('vineyard_id'))
            date_start_str = str(request.args.get('date_start'))
            date_end_str = str(request.args.get('date_end'))
            row_spacing_m = float(request.args.get('row_spacing_m'))
            vine_spacing_m = float(request.args.get('vine_spacing_m'))
            geom_coordinates_str = request.args.get('coordinates')
            geom_coordinates = ast.literal_eval(geom_coordinates_str)

            respose_text = orion_add_block.create_block_entity(str(block_id), vineyard_id, user_defined_id, row_spacing_m, vine_spacing_m, date_start_str, date_end_str, geom_coordinates)

        return render_template('block_add.html',
                               respose_text = respose_text
                               )

    except S3Error as exc:
        return f"Error: {exc}"
    
@app.route('/vinerow', methods=['GET', 'POST'])
def vinerow():
    entity_id = request.args.get('entity_id', 'vinerow001')  # Default to 'vinerow001' if not provided

    try:
        # Get data from Fiware Orion for a specific entity
        fiware_data = get_fiware_entity_data(entity_id)

        # Extract information from Fiware data       
        block_id = fiware_data.get("block_id", {}).get("value")
        user_defined_id = fiware_data.get("user_defined_id", {}).get("value")
        geom = fiware_data.get("geom", {}).get("value")
        coordinates = fiware_data.get("geom", {}).get("value", {}).get("coordinates")
        orientation = fiware_data.get("orientation", {}).get("value")

        # Format coordinates
        #coordinates_formatted = []
        #for sublist in coordinates:
        #    for item in sublist:
        #        coordinates_formatted.append(item)

        # Find all vine_ids and total number of vines given a vine_row_id
        vine_ids, total_grapes_count, total_vine_count = orion_query_vines_in_vine_row.find_vine_ids_grapes_and_total_vines_in_row("Vine", entity_id)

        # find number of grapes over time given a list of vine ids
        aggregated_grape_number, earliest_timestamp = mongodb_access_multiple_vine_data_by_time.aggregate_grapes_over_time(vine_ids, 10)
        aggregated_grape_number = convert_to_unix_time_format(aggregated_grape_number)

        # TODO add error page
        if fiware_data is None:
            error_message = f"Entity with ID '{entity_id}' not found in Fiware Orion."
            #return render_template('index.html', error_message=error_message)

        return render_template('vinerow.html',
                                    entity_id = entity_id,
                                    block_id = block_id,
                                    user_defined_id = user_defined_id,
                                    coordinates = coordinates, # coordinates_formatted,
                                    orientation = orientation,
                                    total_vine_count = total_vine_count,
                                    total_grapes_count = total_grapes_count,
                                    aggregated_grape_number = aggregated_grape_number
                                    )
    
    except S3Error as exc:
        return f"Error: {exc}"
    
@app.route('/vinerow_all', methods=['GET', 'POST'])
def vine_row_all():
    vine_row_coordinates_list = []  # List to store vine row ID and coordinates

    try:
        # Query Orion to get all entities of type "VineRow"
        fiware_orion_url_vine_row = f"{FIWARE_ORION_BASE_URL}?type=VineRow&limit=200"
        vine_row_response = requests.get(fiware_orion_url_vine_row)

        if vine_row_response.status_code == 200:
            vine_row_data = vine_row_response.json()
            for vine_row_entity in vine_row_data:
                vine_row_id = vine_row_entity['id']
                user_defined_id = vine_row_entity['user_defined_id']['value']
                # Extract coordinates
                coordinates = vine_row_entity['geom']['value']['coordinates']

                # Format coordinates
                #coordinates_formatted = []                
                #for sublist in coordinates:
                #    for item in sublist:
                #        coordinates_formatted.append(item)

                vine_row_coordinates_list.append({'vine_row_id': vine_row_id, 'user_defined_id': user_defined_id, 'coordinates': coordinates}) # coordinates_formatted})

            # Sort the list based on user_defined_id values
            vine_row_coordinates_list = sorted(vine_row_coordinates_list, key=lambda x: (int(re.search(r'\d+$', x['user_defined_id']).group()), x['user_defined_id']))

        else:
            print(f"Failed to retrieve vine_row data. Status code: {vine_row_response.status_code}")
        

        return render_template('vinerow_all.html',
                                    vine_row_coordinates_list = vine_row_coordinates_list
                                    )

    except S3Error as exc:
        return f"Error: {exc}"

@app.route('/vinerow_add', methods=['GET', 'POST'])
def vinerow_add():

    try:
        vine_row_id = request.args.get('vine_row_id')

        respose_text = "None"
        
        if vine_row_id:
            # if vine_row_id is not empty
            
            user_defined_id = str(request.args.get('user_defined_id'))
            block_id = str(request.args.get('block_id'))
            geom_coordinates_str = request.args.get('coordinates')
            geom_coordinates = ast.literal_eval(geom_coordinates_str)

            respose_text = orion_add_vinerow.create_vine_row_entity(str(vine_row_id), block_id, user_defined_id, 0, "", "", geom_coordinates)
            

        return render_template('vinerow_add.html',
                               respose_text = respose_text
                               )

    except S3Error as exc:
        return f"Error: {exc}"

@app.route('/mapbox_geojson', methods=['GET', 'POST'])
def mapbox_geojson():        

    return render_template('mapbox_geojson.html')

@app.route('/jojo', methods=['GET', 'POST'])
def jojo():
    vineyard_id = "jojo"

    point_data_list = []  # List to store point data and coordinates
    line_data_list = []  # List to store line data and coordinates
    polygon_data_list = []  # List to store polygon data and coordinates
    vine_row_data_list = []  # List to store vine row ID and coordinates
    vine_row_coordinates_list = []
    anchor_post_line_coordinates_list = []
    anchor_post_points_coordinates_list = []
    under_vine_coordinates_list = []
    mid_row_line_coordinates_list = []
    mid_row_area_coordinates_list = []
    vine_coordinates_list = []
    block_data_list = []  # List to store block ID and coordinates
    vineyard_data_list = []  # List to store vineyard data
    vineyard_area = 0
    vineyard_total_rows = 0
    vineyard_total_row_length = 0
    vineyard_total_vines = 0
    under_vine_area = 0
    mid_row_area = 0

    anchor_post_distance = 1.0 # metres, distacne from end post to anchor post
    mid_row_width = 1.0 # metres
    under_vine_width = 0.5 # metres, under vine width only on one side of vine row
    vine_spacing = 1.0 # metres, vine spacing alony rows
    vine_spacing_initial_offset = 1.0  # metres, spacing of first vine along rows
    vine_spacing_last_offset = 1.0  # metres, spacing of last vine along rows

    try:
        # Query Orion to get all entities of type "point"
        fiware_orion_url_point = f"{FIWARE_ORION_BASE_URL}?type=point&q=vineyard_id=={vineyard_id}"
        point_response = requests.get(fiware_orion_url_point)

        if point_response.status_code == 200:
            point_data = point_response.json()
            for point_entity in point_data:
                point_id = point_entity['id']
                name = point_entity['name']['value']
                category = point_entity['category']['value']
                class_string = point_entity['class']['value']
                coordinates = point_entity['location']['value']['coordinates']

                point_data_list.append({'point_id': point_id, 'name': name, 'category': category, 'class_string': class_string, 'coordinates': coordinates, 'type': 'Point'})
        else:
            print(f"Failed to retrieve point data. Status code: {point_response.status_code}")

        # Query Orion to get all entities of type "line"
        fiware_orion_url_line = f"{FIWARE_ORION_BASE_URL}?type=line&q=vineyard_id=={vineyard_id}"
        line_response = requests.get(fiware_orion_url_line)

        if line_response.status_code == 200:
            line_data = line_response.json()
            for line_entity in line_data:
                line_id = line_entity['id']
                name = line_entity['name']['value']
                category = line_entity['category']['value']
                class_string = line_entity['class']['value']
                coordinates = line_entity['geom']['value']['coordinates']
                length = calculate_line_length(coordinates)

                line_data_list.append({'line_id': line_id, 'name': name, 'category': category, 'class_string': class_string, 'coordinates': coordinates, 'length': round(abs(length), 2), 'type': 'LineString'})
        else:
            print(f"Failed to retrieve line data. Status code: {line_response.status_code}")

        # Query Orion to get all entities of type "polygon"
        fiware_orion_url_polygon = f"{FIWARE_ORION_BASE_URL}?type=polygon&q=vineyard_id=={vineyard_id}"
        polygon_response = requests.get(fiware_orion_url_polygon)

        if polygon_response.status_code == 200:
            polygon_data = polygon_response.json()
            for polygon_entity in polygon_data:
                polygon_id = polygon_entity['id']
                name = polygon_entity['name']['value']
                category = polygon_entity['category']['value']
                class_string = polygon_entity['class']['value']
                coordinates = polygon_entity['geom']['value']['coordinates']
                area, perimeter = calculate_polygon_area(coordinates)

                polygon_data_list.append({'polygon_id': polygon_id, 'name': name, 'category': category, 'class_string': class_string, 'coordinates': coordinates, 'area': round(abs(area), 2), 'perimeter': round(perimeter, 2), 'type': 'Polygon'})
        else:
            print(f"Failed to retrieve point data. Status code: {polygon_response.status_code}")

        # Query Orion to get all entities of type "VineRow"
        fiware_orion_url_vine_row = f"{FIWARE_ORION_BASE_URL}?type=VineRow&offset=7&limit=92" # ?type=VineRow&limit=200"
        vine_row_response = requests.get(fiware_orion_url_vine_row)

        if vine_row_response.status_code == 200:
            vine_row_data = vine_row_response.json()
            vine_id_number = 0            
            for vine_row_entity in vine_row_data:
                vine_row_id = vine_row_entity['id']
                user_defined_id = vine_row_entity['user_defined_id']['value']
                block_id = vine_row_entity['block_id']['value']
                coordinates = vine_row_entity['geom']['value']['coordinates']
                length = calculate_line_length(coordinates)
                anchor_post_lines = extend_line.extend_line(coordinates, anchor_post_distance) # (line coordinates, distance to entend line) anchor post locations are anchor_post_lines[0][0] anchor_post_lines[1][1]
                under_vine_polygon_coordinates, area = line_to_polygon.generate_polygon(coordinates, under_vine_width) # (line coordinates, width (m) of undervine on one side of row) area in m^2
                under_vine_area = under_vine_area + area

                # vine_row_coordinates_list.append(coordinates)
                anchor_post_line_coordinates_list.append({'anchor_post_line_id': str(vine_row_id + "anchor_line_a"), 'coordinates': anchor_post_lines[0], 'type': 'LineString'})
                anchor_post_line_coordinates_list.append({'anchor_post_line_id': str(vine_row_id + "anchor_line_b"), 'coordinates': anchor_post_lines[1], 'type': 'LineString'})
                anchor_post_points_coordinates_list.append({'anchor_post_point_id': str(vine_row_id + "anchor_post_a"), 'coordinates': anchor_post_lines[0][0], 'type': 'Point'})
                anchor_post_points_coordinates_list.append({'anchor_post_point_id': str(vine_row_id + "anchor_post_b"), 'coordinates': anchor_post_lines[1][1], 'type': 'Point'})

                under_vine_coordinates_list.append({'under_vine_id': str(vine_row_id + '_under_vine'), 'coordinates': under_vine_polygon_coordinates, 'area': round(area, 2), 'block_id': block_id, 'type': 'Polygon'})
        
                vine_coordinates_along_row = interpolate_points.interpolate_points(coordinates, vine_spacing, vine_spacing_initial_offset, vine_spacing_last_offset)

                for vine_coordinates in vine_coordinates_along_row:
                    vine_coordinates_list.append({'vine_id': str(user_defined_id + '_vine_' + str(vine_id_number)), 'coordinates': vine_coordinates, 'type': 'Point'})
                    vine_id_number += 1

                vine_row_data_list.append({'vine_row_id': vine_row_id, 'user_defined_id': user_defined_id, 'block_id': block_id, 'coordinates': coordinates, 'length': round(abs(length), 2), 'number_of_vines': vine_id_number, 'type': 'LineString'})
                
                vine_id_number = 0

                # Sort the list based on user_defined_id values, depends on the user_defined_id having assending numbers
                vine_row_data_list = sorted(vine_row_data_list, key=lambda x: (int(re.search(r'\d+$', x['user_defined_id']).group()), x['user_defined_id']))

        else:
            print(f"Failed to retrieve vine_row data. Status code: {vine_row_response.status_code}")
  
        # Calculate mid row line coordinates
        for row in range(len(vine_row_data_list) - 1):
            block_id = vine_row_data_list[row]['block_id']
            row1_id = vine_row_data_list[row]['user_defined_id']
            row2_id = vine_row_data_list[row + 1]['user_defined_id']
            row1_coords = vine_row_data_list[row]['coordinates']
            row2_coords = vine_row_data_list[row + 1]['coordinates']
            mid_point1 = [(row1_coords[0][0] + row2_coords[0][0]) / 2, (row1_coords[0][1] + row2_coords[0][1]) / 2]
            mid_point2 = [(row1_coords[-1][0] + row2_coords[-1][0]) / 2, (row1_coords[-1][1] + row2_coords[-1][1]) / 2]

            mid_row_area_coordinates, area = line_to_polygon.generate_polygon([mid_point1, mid_point2], mid_row_width) # (line coordinates, width (m) of mid row) area in m^2
            mid_row_area = mid_row_area + area

            mid_row_line_coordinates_list.append({'mid_row_line_id': str(row1_id + '_to_' + row2_id + '_mid_row_line'), 'coordinates': [mid_point1, mid_point2], 'type': 'LineString'})
            mid_row_area_coordinates_list.append({'mid_row_area_id': str(row1_id + '_to_' + row2_id + '_mid_row_area'), 'coordinates': mid_row_area_coordinates, 'area': round(area, 2), 'block_id': block_id, 'type': 'Polygon'})

        # Query Orion to get all entities of type "Block"
        fiware_orion_url_block = f"{FIWARE_ORION_BASE_URL}?type=Block&q=vineyard_id==jojo&limit=50"
        block_response = requests.get(fiware_orion_url_block)

        if block_response.status_code == 200:
            block_data = block_response.json()
            for block_entity in block_data:
                block_id = block_entity['id']
                user_defined_id = block_entity['user_defined_id']['value']
                name = block_entity['name']['value']
                variety = block_entity['variety']['value']
                anchor_post_distance = vine_row_entity['anchor_post_distance']['value']
                under_vine_width = vine_row_entity['under_vine_width']['value']
                vine_spacing = vine_row_entity['vine_spacing']['value']
                coordinates = block_entity['geom']['value']['coordinates']
                area, perimeter = calculate_polygon_area(coordinates)

                total_rows, total_row_length = get_row_info(vine_row_data_list, user_defined_id)

                under_vine_area_block = 0
                for item in under_vine_coordinates_list:
                    if item['block_id'] == user_defined_id:
                            under_vine_area_block = under_vine_area_block + item['area']

                mid_row_area_block = 0
                for item in mid_row_area_coordinates_list:
                    if item['block_id'] == user_defined_id:
                            mid_row_area_block = mid_row_area_block + item['area']

                number_of_vines_in_block = 0
                for item in vine_row_data_list:
                    if item['block_id'] == user_defined_id:
                            number_of_vines_in_block = number_of_vines_in_block + item['number_of_vines']                

                block_data_list.append({'block_id': block_id, 'user_defined_id': user_defined_id, 'name': name, 'variety': variety, 'coordinates': coordinates, 'area': round(abs(area), 2), 
                                        'perimeter': round(perimeter, 2), 'total_rows': total_rows, 'total_row_length': round(total_row_length, 2), 
                                        'under_vine_area_block': round(under_vine_area_block, 2), 'mid_row_area_block': round(mid_row_area_block, 2), 
                                        'number_of_vines_in_block': number_of_vines_in_block, 
                                        'anchor_post_distance': anchor_post_distance,
                                        'under_vine_width': under_vine_width,
                                        'vine_spacing': vine_spacing,
                                        'type': 'Polygon'})
                
                vineyard_area = vineyard_area + abs(area)
                vineyard_total_rows = vineyard_total_rows + total_rows
                vineyard_total_row_length = vineyard_total_row_length + total_row_length
                vineyard_total_vines = vineyard_total_vines + number_of_vines_in_block
        else:
            print(f"Failed to retrieve block data. Status code: {block_response.status_code}")

        # Export selected check boxes to geojson
        if request.method == 'POST':
            if 'button_export_to_geojson' in request.form: # If request is to export to GeoJSON
                data_lists = []

                if request.form.get("showBlocks"):
                    data_lists.append(block_data_list)
                if request.form.get("showVineRows"):
                    data_lists.append(vine_row_data_list)
                if request.form.get("showVines"):
                    data_lists.append(vine_coordinates_list) 
                if request.form.get("showAnchorPosts"):
                    data_lists.append(anchor_post_points_coordinates_list)
                if request.form.get("showAnchorLines"):
                    data_lists.append(anchor_post_line_coordinates_list)
                if request.form.get("showUnderVineAreas"):
                    data_lists.append(under_vine_coordinates_list)
                if request.form.get("showMidRowLines"):
                    data_lists.append(mid_row_line_coordinates_list)
                if request.form.get("showMidRowAreas"):
                    data_lists.append(mid_row_area_coordinates_list)
                if request.form.get("showPoints"):
                    data_lists.append(point_data_list)
                if request.form.get("showLines"):
                    data_lists.append(line_data_list)
                if request.form.get("showPolygons"):
                    data_lists.append(polygon_data_list)   

                geojson_file = export_to_geojson.create_geojson(data_lists)

                json_bytes = geojson_file.encode('utf-8')
                bytes_io = BytesIO(json_bytes)
                bytes_io.seek(0)

                # Return the file as a response
                # return send_file("data/output.geojson", as_attachment=True)
                return send_file(bytes_io, as_attachment = True, attachment_filename = vineyard_id + ".geojson", mimetype = 'application/json')            
            
            elif 'button_export_to_antobot_xml' in request.form: # If request is to export to antobot XML format
                # test_file_content = "This is a test file for Antobot XML export."
                # bytes_io = BytesIO(test_file_content.encode('utf-8'))
                # bytes_io.seek(0)

                xml_file = export_to_antobot_xml.coordinates_to_xml(mid_row_line_coordinates_list) # Takes a list of coordinate paris of the end potins of the mid row lines 
                xml_bytes = BytesIO(xml_file.encode())

                return send_file(xml_bytes, as_attachment=True, attachment_filename=vineyard_id + "_antobot.xml", mimetype='text/plain')
            
        # Convert vine locations to geojson and send to mapbox
        # TODO convert all map data to geojson and send to mapbox rather than lists
        # vine_coordinates_geojson_file = vine_list_to_geojson.vine_list_to_geojson(vine_coordinates_list)
        data_lists = []
        data_lists.append(vine_coordinates_list)
        vine_coordinates_geojson_file = export_to_geojson.create_geojson(data_lists)

        return render_template('jojo.html',
                            point_data_list = point_data_list,
                            line_data_list = line_data_list,
                            polygon_data_list = polygon_data_list,
                            vine_row_data_list = vine_row_data_list,
                            block_data_list = block_data_list,
                            vineyard_area =  round(vineyard_area, 2),
                            vineyard_total_rows = vineyard_total_rows,
                            vineyard_total_row_length = vineyard_total_row_length,
                            #polygons = polygons,
                            anchor_post_line_coordinates_list = anchor_post_line_coordinates_list,
                            anchor_post_points_coordinates_list = anchor_post_points_coordinates_list,
                            under_vine_coordinates_list = under_vine_coordinates_list,
                            under_vine_area = round(under_vine_area, 2),
                            mid_row_line_coordinates_list = mid_row_line_coordinates_list,
                            mid_row_area_coordinates_list = mid_row_area_coordinates_list,
                            mid_row_area = round(mid_row_area, 2),
                            vine_coordinates_list = vine_coordinates_list,
                            vine_coordinates_geojson_file = vine_coordinates_geojson_file,
                            vineyard_total_vines = vineyard_total_vines
                            )
    
    except S3Error as exc:
        return f"Error: {exc}"  

@app.route('/vineyard_geojson_orion', methods=['GET', 'POST'])
def vineyard_geojson_orion():
    #vineyard_id = "jojo"
    #if request.method == 'POST':
    #    if 'button_vineyard_select' in request.form: # If request is to view vineyard
    vineyard_id = selected_vineyard_id = request.form.get('vineyard_id', 'riseholme')  # Get the selected vineyard_id from the HTML form

    all_vineyard_data_list = [] # List to store vineyard data
    vineyard_data_list = [] # List to store vineyard data
    point_data_list = [] # List to store point data and coordinates
    line_data_list = [] # List to store line data and coordinates
    polygon_data_list = [] # List to store polygon data and coordinates
    vine_row_data_list = [] # List to store vine row ID and coordinates
    vine_row_coordinates_list = []
    anchor_post_line_coordinates_list = []
    anchor_post_points_coordinates_list = []
    under_vine_coordinates_list = []
    mid_row_line_coordinates_list = []
    mid_row_area_coordinates_list = []
    vine_coordinates_list = []
    block_data_list = []  # List to store block ID and coordinates
    block_area_data_list = []  # List to store block ID and coordinates
    vineyard_data_list = []  # List to store vineyard data
    vineyard_area = 0
    vineyard_total_rows = 0
    vineyard_total_row_length = 0
    vineyard_total_vines = 0
    under_vine_area = 0
    mid_row_area = 0

    #anchor_post_distance = 1.0 # metres, distacne from end post to anchor post
    mid_row_width = 1.0 # metres
    #under_vine_width = 0.5 # metres, under vine width only on one side of vine row
    #vine_spacing = 1.0 # metres, vine spacing alony rows
    #vine_spacing_initial_offset = 1.0  # metres, spacing of first vine along rows
    #vine_spacing_last_offset = 1.0  # metres, spacing of last vine along rows

    try:
        # Query Orion to get ALL entities of type "Vineyard"
        fiware_orion_url_point = f"{FIWARE_ORION_BASE_URL}?type=Vineyard"
        all_vineyard_response = requests.get(fiware_orion_url_point)

        if all_vineyard_response.status_code == 200:
            all_vineyard_data = all_vineyard_response.json()
            for all_vineyard_entity in all_vineyard_data:
                all_id = all_vineyard_entity['id']
                all_vineyard_id = all_vineyard_entity['vineyard_id']['value']
                all_name = all_vineyard_entity['name']['value']
                all_street_address = all_vineyard_entity['street_address']['value']
                all_owner = all_vineyard_entity['owner']['value']
                all_coordinates = all_vineyard_entity['geom']['value']['coordinates']

                all_vineyard_data_list.append({'id': all_id, 'vineyard_id': all_vineyard_id, 'name': all_name, 'street_address': all_street_address,  'owner': all_owner, 'coordinates': all_coordinates, 'type': 'Polygon'})
        else:
            print(f"Failed to retrieve vineyard data. Status code: {all_vineyard_response.status_code}")


        # Query Orion to get entities of type "Vineyard" with vineyard_id
        fiware_orion_url_point = f"{FIWARE_ORION_BASE_URL}?type=Vineyard&q=vineyard_id=={vineyard_id}"
        vineyard_response = requests.get(fiware_orion_url_point)

        if vineyard_response.status_code == 200:
            vineyard_data = vineyard_response.json()
            for vineyard_entity in vineyard_data:
                id = vineyard_entity['id']
                vineyard_id = vineyard_entity['vineyard_id']['value']
                name = vineyard_entity['name']['value']
                street_address = vineyard_entity['street_address']['value']
                owner = vineyard_entity['owner']['value']
                coordinates = vineyard_entity['geom']['value']['coordinates']
                area, perimeter = calculate_polygon_area(coordinates)

                vineyard_data_list.append({'id': id, 'vineyard_id': vineyard_id, 'name': name, 'street_address': street_address,  'owner': owner, 'coordinates': coordinates, 'area': abs(round(area, 2)), 'perimeter': round(perimeter, 2), 'type': 'Polygon'})
        else:
            print(f"Failed to retrieve vineyard data. Status code: {all_vineyard_response.status_code}")

        # Query Orion to get all entities of type "point"
        fiware_orion_url_point = f"{FIWARE_ORION_BASE_URL}?type=point&q=vineyard_id=={vineyard_id}"
        point_response = requests.get(fiware_orion_url_point)

        if point_response.status_code == 200:
            point_data = point_response.json()
            for point_entity in point_data:
                point_id = point_entity['id']
                name = point_entity['name']['value']
                category = point_entity['category']['value']
                class_string = point_entity['class']['value']
                coordinates = point_entity['location']['value']['coordinates']

                point_data_list.append({'point_id': point_id, 'name': name, 'category': category, 'class_string': class_string, 'coordinates': coordinates, 'feature_type': 'point', 'type': 'Point'})
        else:
            print(f"Failed to retrieve point data. Status code: {point_response.status_code}")

        # Query Orion to get all entities of type "line"
        fiware_orion_url_line = f"{FIWARE_ORION_BASE_URL}?type=line&q=vineyard_id=={vineyard_id}"
        line_response = requests.get(fiware_orion_url_line)

        if line_response.status_code == 200:
            line_data = line_response.json()
            for line_entity in line_data:
                line_id = line_entity['id']
                name = line_entity['name']['value']
                category = line_entity['category']['value']
                class_string = line_entity['class']['value']
                coordinates = line_entity['geom']['value']['coordinates']
                length = calculate_line_length(coordinates)

                line_data_list.append({'line_id': line_id, 'name': name, 'category': category, 'class_string': class_string, 'coordinates': coordinates, 'length': round(abs(length), 2), 'feature_type': 'line', 'type': 'LineString'})
        else:
            print(f"Failed to retrieve line data. Status code: {line_response.status_code}")

        # Query Orion to get all entities of type "polygon"
        fiware_orion_url_polygon = f"{FIWARE_ORION_BASE_URL}?type=polygon&q=vineyard_id=={vineyard_id}"
        polygon_response = requests.get(fiware_orion_url_polygon)

        if polygon_response.status_code == 200:
            polygon_data = polygon_response.json()
            for polygon_entity in polygon_data:
                polygon_id = polygon_entity['id']
                name = polygon_entity['name']['value']
                category = polygon_entity['category']['value']
                class_string = polygon_entity['class']['value']
                coordinates = polygon_entity['geom']['value']['coordinates']
                area, perimeter = calculate_polygon_area(coordinates)

                polygon_data_list.append({'polygon_id': polygon_id, 'name': name, 'category': category, 'class_string': class_string, 'coordinates': coordinates, 'area': round(abs(area), 2), 'perimeter': round(perimeter, 2), 'feature_type': 'polygon', 'type': 'Polygon'})
        else:
            print(f"Failed to retrieve point data. Status code: {polygon_response.status_code}")

        # Query Orion to get all entities of type "VineRow"
        #fiware_orion_url_vine_row = f"{FIWARE_ORION_BASE_URL}?type=VineRow&offset=7&limit=92" # ?type=VineRow&limit=200"
        fiware_orion_url_vine_row = f"{FIWARE_ORION_BASE_URL}?type=VineRow&q=vineyard_id=={vineyard_id}&limit=200" # ?type=VineRow&limit=200"
        vine_row_response = requests.get(fiware_orion_url_vine_row)

        if vine_row_response.status_code == 200:
            vine_row_data = vine_row_response.json()
            vine_id_number = 0            
            for vine_row_entity in vine_row_data:
                vine_row_id = vine_row_entity['id']
                user_defined_id = vine_row_entity['user_defined_id']['value']
                block_id = vine_row_entity['block_id']['value']
                coordinates = vine_row_entity['geom']['value']['coordinates']
                anchor_post_distance = vine_row_entity['anchor_post_distance']['value']
                under_vine_width = vine_row_entity['under_vine_width']['value']
                vine_spacing = vine_row_entity['vine_spacing']['value']
                length = calculate_line_length(coordinates)
                anchor_post_lines = extend_line.extend_line(coordinates, anchor_post_distance) # (line coordinates, distance to entend line) anchor post locations are anchor_post_lines[0][0] anchor_post_lines[1][1]
                under_vine_polygon_coordinates, area = line_to_polygon.generate_polygon(coordinates, under_vine_width) # (line coordinates, width (m) of undervine on one side of row) area in m^2
                under_vine_area = under_vine_area + area

                # vine_row_coordinates_list.append(coordinates)
                anchor_post_line_coordinates_list.append({'anchor_post_line_id': str(vine_row_id + "anchor_line_a"), 'coordinates': anchor_post_lines[0], 'feature_type': 'anchor_post_line', 'type': 'LineString'})
                anchor_post_line_coordinates_list.append({'anchor_post_line_id': str(vine_row_id + "anchor_line_b"), 'coordinates': anchor_post_lines[1], 'feature_type': 'anchor_post_line', 'type': 'LineString'})
                anchor_post_points_coordinates_list.append({'anchor_post_point_id': str(vine_row_id + "anchor_post_a"), 'coordinates': anchor_post_lines[0][0], 'feature_type': 'anchor_post', 'type': 'Point'})
                anchor_post_points_coordinates_list.append({'anchor_post_point_id': str(vine_row_id + "anchor_post_b"), 'coordinates': anchor_post_lines[1][1], 'feature_type': 'anchor_post', 'type': 'Point'})

                under_vine_coordinates_list.append({'under_vine_id': str(vine_row_id + '_under_vine'), 'coordinates': under_vine_polygon_coordinates, 'area': round(area, 2), 'block_id': block_id, 'type': 'Polygon'})
        
                vine_coordinates_along_row = interpolate_points.interpolate_points(coordinates, vine_spacing, vine_spacing, vine_spacing) # coordinates, vine_spacing, vine_spacing_initial_offset, vine_spacing_last_offset

                for vine_coordinates in vine_coordinates_along_row:
                    # vine_coordinates_list.append({'vine_id': str(user_defined_id + '_vine_' + str(vine_id_number)), 'coordinates': vine_coordinates, 'type': 'Point'})
                    grape_number = random.randint(10, 50)
                    vine_coordinates_list.append({'vine_id': str(user_defined_id + '_vine_' + str(vine_id_number)), 'coordinates': vine_coordinates, 'grape_number': grape_number, 'type': 'Point'})
                    vine_id_number += 1

                vine_row_data_list.append({'vine_row_id': vine_row_id, 
                                           'user_defined_id': user_defined_id, 
                                           'block_id': block_id, 
                                           'coordinates': coordinates, 
                                           'length': round(abs(length), 2), 
                                           'number_of_vines': vine_id_number, 
                                           'anchor_post_distance': anchor_post_distance,
                                           'under_vine_width': under_vine_width,
                                           'vine_spacing': vine_spacing,
                                           'feature_type': 'row',
                                           'type': 'LineString'})
                
                vine_id_number = 0

                # Sort the list based on user_defined_id values, depends on the user_defined_id having assending numbers
                vine_row_data_list = sorted(vine_row_data_list, key=lambda x: (int(re.search(r'\d+$', x['user_defined_id']).group()), x['user_defined_id']))

        else:
            print(f"Failed to retrieve vine_row data. Status code: {vine_row_response.status_code}")
  
        # Calculate mid row line coordinates
        for row in range(len(vine_row_data_list) - 1):
            block_id = vine_row_data_list[row]['block_id']
            row1_id = vine_row_data_list[row]['user_defined_id']
            row2_id = vine_row_data_list[row + 1]['user_defined_id']
            row1_coords = vine_row_data_list[row]['coordinates']
            row2_coords = vine_row_data_list[row + 1]['coordinates']
            mid_point1 = [(row1_coords[0][0] + row2_coords[0][0]) / 2, (row1_coords[0][1] + row2_coords[0][1]) / 2]
            mid_point2 = [(row1_coords[-1][0] + row2_coords[-1][0]) / 2, (row1_coords[-1][1] + row2_coords[-1][1]) / 2]            
            mid_row_line_length = calculate_line_length([mid_point1, mid_point2])

            mid_row_area_coordinates, area = line_to_polygon.generate_polygon([mid_point1, mid_point2], mid_row_width) # (line coordinates, width (m) of mid row) area in m^2
            mid_row_area = mid_row_area + area

            mid_row_line_coordinates_list.append({'mid_row_line_id': str(row1_id + '_to_' + row2_id + '_mid_row_line'), 'coordinates': [mid_point1, mid_point2], 'length': round(abs(mid_row_line_length), 2), 'feature_type': 'mid_row_line', 'type': 'LineString'})
            mid_row_area_coordinates_list.append({'mid_row_area_id': str(row1_id + '_to_' + row2_id + '_mid_row_area'), 'coordinates': mid_row_area_coordinates, 'area': round(area, 2), 'block_id': block_id, 'feature_type': 'mid_row_area', 'type': 'Polygon'})

        # Query Orion to get all entities of type "Block"
        fiware_orion_url_block = f"{FIWARE_ORION_BASE_URL}?type=Block&q=vineyard_id=={vineyard_id}&limit=200"
        block_response = requests.get(fiware_orion_url_block)

        if block_response.status_code == 200:
            block_data = block_response.json()
            for block_entity in block_data:
                block_id = block_entity['id']
                user_defined_id = block_entity['user_defined_id']['value']
                name = block_entity['name']['value']
                variety = block_entity['variety']['value']
                anchor_post_distance = vine_row_entity['anchor_post_distance']['value']
                under_vine_width = vine_row_entity['under_vine_width']['value']
                vine_spacing = vine_row_entity['vine_spacing']['value']
                coordinates = block_entity['geom']['value']['coordinates']
                area, perimeter = calculate_polygon_area(coordinates)

                total_rows, total_row_length = get_row_info(vine_row_data_list, user_defined_id)

                under_vine_area_block = 0
                for item in under_vine_coordinates_list:
                    if item['block_id'] == user_defined_id:
                            under_vine_area_block = under_vine_area_block + item['area']

                mid_row_area_block = 0
                for item in mid_row_area_coordinates_list:
                    if item['block_id'] == user_defined_id:
                            mid_row_area_block = mid_row_area_block + item['area']

                number_of_vines_in_block = 0
                for item in vine_row_data_list:
                    if item['block_id'] == user_defined_id:
                            number_of_vines_in_block = number_of_vines_in_block + item['number_of_vines']

                block_data_list.append({'block_id': block_id, 'user_defined_id': user_defined_id, 'name': name, 'variety': variety, 'coordinates': coordinates, 'area': round(abs(area), 2), 
                                        'perimeter': round(perimeter, 2), 'total_rows': total_rows, 'total_row_length': round(total_row_length, 2), 
                                        'under_vine_area_block': round(under_vine_area_block, 2), 'mid_row_area_block': round(mid_row_area_block, 2), 
                                        'number_of_vines_in_block': number_of_vines_in_block, 
                                        'anchor_post_distance': anchor_post_distance,
                                        'under_vine_width': under_vine_width,
                                        'vine_spacing': vine_spacing,
                                        'feature_type': 'block',
                                        'type': 'Polygon'})
                
                vineyard_area = vineyard_area + abs(area)
                vineyard_total_rows = vineyard_total_rows + total_rows
                vineyard_total_row_length = vineyard_total_row_length + total_row_length
                vineyard_total_vines = vineyard_total_vines + number_of_vines_in_block
        else:
            print(f"Failed to retrieve block data. Status code: {block_response.status_code}")

        # Query Orion to get all entities of type "BlockArea"
        fiware_orion_url_block_area = f"{FIWARE_ORION_BASE_URL}?type=BlockArea&q=vineyard_id=={vineyard_id}&limit=200"
        block_area_response = requests.get(fiware_orion_url_block_area)

        if block_area_response.status_code == 200:
            block_area_data = block_area_response.json()
            for block_area_entity in block_area_data:
                block_area_id = block_area_entity['id']
                user_defined_id = block_area_entity['user_defined_id']['value']
                name = block_area_entity['name']['value']
                coordinates = block_area_entity['geom']['value']['coordinates']
                area, perimeter = calculate_polygon_area(coordinates)

                block_area_data_list.append({'block_area_id': block_area_id, 'user_defined_id': user_defined_id, 'name': name, 'coordinates': coordinates, 'area': round(abs(area), 2), 
                                        'perimeter': round(perimeter, 2),
                                        'feature_type': 'block_area',
                                        'type': 'Polygon'})                
        else:
            print(f"Failed to retrieve block area data. Status code: {block_area_response.status_code}")

        topo_map_extend_distance = 3
        topo_map_node_spacing_along_row = 10
        topo_map_node_spacing_row_initial_offset = 10
        topo_map_node_spacing_row_last_offset = 10
        topo_map_row_width = 6

        # mid_row_line_coordinates_list, distance to extend the points from the mid row line, node_spacing_along_row, node_spacing_row_initial_offset, node_spacing_row_last_offset, row_width
        topo_map_point_list, topo_map_line_list, topo_map_interpolated_nodes = generate_topological_map.extend_line_points(mid_row_line_coordinates_list, topo_map_extend_distance, topo_map_node_spacing_along_row, topo_map_node_spacing_row_initial_offset, topo_map_node_spacing_row_last_offset, topo_map_row_width) 

        # Convert data to geojson and send to mapbox
        data_lists = []
        data_lists.append(vineyard_data_list)
        data_lists.append(block_data_list)
        data_lists.append(block_area_data_list)
        data_lists.append(vine_row_data_list)
        data_lists.append(vine_coordinates_list) 
        data_lists.append(anchor_post_points_coordinates_list)
        data_lists.append(anchor_post_line_coordinates_list)
        data_lists.append(under_vine_coordinates_list)
        data_lists.append(mid_row_line_coordinates_list)
        data_lists.append(mid_row_area_coordinates_list)
        data_lists.append(point_data_list)
        data_lists.append(line_data_list)
        data_lists.append(polygon_data_list)
        data_lists.append(topo_map_point_list)
        data_lists.append(topo_map_line_list)
        data_lists.append(topo_map_interpolated_nodes)

        geojson_data = export_to_geojson.create_geojson(data_lists)

        vine_row_boundaries = create_enclosing_polygons.create_enclosing_polygons(geojson_data)

        # Export selected check boxes to geojson
        if request.method == 'POST':
            if 'button_export_to_geojson' in request.form: # If request is to export to GeoJSON
                data_lists = []

                if request.form.get("showBlocks"):
                    data_lists.append(block_data_list)
                if request.form.get("showVineRows"):
                    data_lists.append(vine_row_data_list)
                if request.form.get("showVines"):
                    data_lists.append(vine_coordinates_list) 
                if request.form.get("showAnchorPosts"):
                    data_lists.append(anchor_post_points_coordinates_list)
                if request.form.get("showAnchorLines"):
                    data_lists.append(anchor_post_line_coordinates_list)
                if request.form.get("showUnderVineAreas"):
                    data_lists.append(under_vine_coordinates_list)
                if request.form.get("showMidRowLines"):
                    data_lists.append(mid_row_line_coordinates_list)
                if request.form.get("showMidRowAreas"):
                    data_lists.append(mid_row_area_coordinates_list)
                if request.form.get("showTopologicalMap"):
                    data_lists.append(topo_map_point_list)
                    data_lists.append(topo_map_line_list)
                    data_lists.append(topo_map_interpolated_nodes)
                if request.form.get("showPoints"):
                    data_lists.append(point_data_list)
                if request.form.get("showLines"):
                    data_lists.append(line_data_list)
                if request.form.get("showPolygons"):
                    data_lists.append(polygon_data_list)

                geojson_file = export_to_geojson.create_geojson(data_lists)

                json_bytes = geojson_file.encode('utf-8')
                bytes_io = BytesIO(json_bytes)
                bytes_io.seek(0)

                # Return the file as a response
                # return send_file("data/output.geojson", as_attachment=True)
                return send_file(bytes_io, as_attachment = True, attachment_filename = vineyard_id + ".geojson", mimetype = 'application/json')
            
            elif 'button_export_to_antobot_xml' in request.form: # If request is to export to antobot XML format
                # test_file_content = "This is a test file for Antobot XML export."
                # bytes_io = BytesIO(test_file_content.encode('utf-8'))
                # bytes_io.seek(0)

                xml_file = export_to_antobot_xml.coordinates_to_xml(mid_row_line_coordinates_list, mid_row_width) # Takes a list of coordinate paris of the end potins of the mid row lines 
                xml_bytes = BytesIO(xml_file.encode())

                return send_file(xml_bytes, as_attachment=True, attachment_filename=vineyard_id + "_antobot.xml", mimetype='text/plain')
            
            elif 'button_export_to_pdf' in request.form: # If request is to export to pdf                
                pdf_content = export_to_pdf.create_pdf(block_data_list, vineyard_data_list[0]['name'], round(vineyard_area, 2), vineyard_total_rows, vineyard_total_row_length, round(under_vine_area, 2), round(mid_row_area, 2), vineyard_total_vines, vineyard_data_list[0]['street_address'], vineyard_data_list[0]['owner'])

                # Create a BytesIO object from the PDF content
                pdf_io = BytesIO(pdf_content)
                pdf_io.seek(0)

                return send_file(pdf_io, as_attachment=True, attachment_filename=vineyard_id + "_data.pdf", mimetype='application/pdf')
            
            elif 'button_export_vine_row_boundaries' in request.form: # If request is to export to pdf                
                json_bytes = vine_row_boundaries.encode('utf-8')
                bytes_io = BytesIO(json_bytes)
                bytes_io.seek(0)

                return send_file(bytes_io, as_attachment=True, attachment_filename=vineyard_id + "_vine_row_boundaries.geojson", mimetype = 'application/json')
            
            elif 'button_export_to_topological_map' in request.form: # If request is to export to topological map                
                kml_file = export_to_kml.create_kml(topo_map_point_list + topo_map_interpolated_nodes, topo_map_line_list)

                kml_bytes = kml_file.encode('utf-8')
    
                # Creating BytesIO object to store the bytes
                kml_bytes_io = BytesIO()
                kml_bytes_io.write(kml_bytes)
                kml_bytes_io.seek(0)

                center_coordinates = export_to_topological_map.find_centre(topo_map_point_list, topo_map_line_list)

                datum = {'datum_latitude': center_coordinates[0], 'datum_longitude': center_coordinates[1]}

                tmap_yaml_file = topological_map_scripts.kml_to_tmap.run({'src': kml_bytes_io, 'datum': datum, 'location_name':vineyard_id, 'line_col':'ff2f2fd3', 'line_width':'4', 'fill_col':'c02f2fd3', 'shape_size':0.000005})                
                       
                tmap_yaml_bytes = BytesIO(tmap_yaml_file.encode('utf-8'))

                return send_file(tmap_yaml_bytes, as_attachment=True, attachment_filename=vineyard_id + ".tmap2.yaml", mimetype='text/yaml')

            elif 'button_export_to_topological_map_datum' in request.form: # If request is to export to topological map
                yaml_datum = export_to_topological_map.export_to_topological_map_datum(topo_map_point_list, topo_map_line_list)
                
                # Convert YAML content to bytes
                yaml_datum_bytes = BytesIO(yaml_datum.encode('utf-8'))

                return send_file(yaml_datum_bytes, as_attachment=True, attachment_filename=vineyard_id + "_datum.yaml", mimetype='text/yaml')
            
            elif 'button_export_to_kml' in request.form: # If request is to export to KML                
                kml_data_lists = []

                if request.form.get("showBlocks"):
                    kml_data_lists.append(block_data_list)
                if request.form.get("showVineRows"):
                    kml_data_lists.append(vine_row_data_list)
                if request.form.get("showVines"):
                    kml_data_lists.append(vine_coordinates_list) 
                if request.form.get("showAnchorPosts"):
                    kml_data_lists.append(anchor_post_points_coordinates_list)
                if request.form.get("showAnchorLines"):
                    kml_data_lists.append(anchor_post_line_coordinates_list)
                if request.form.get("showUnderVineAreas"):
                    kml_data_lists.append(under_vine_coordinates_list)
                if request.form.get("showMidRowLines"):
                    kml_data_lists.append(mid_row_line_coordinates_list)
                if request.form.get("showMidRowAreas"):
                    kml_data_lists.append(mid_row_area_coordinates_list)
                if request.form.get("showTopologicalMap"):
                    kml_data_lists.append(topo_map_point_list)
                    kml_data_lists.append(topo_map_line_list)
                    kml_data_lists.append(topo_map_interpolated_nodes)
                if request.form.get("showPoints"):
                    kml_data_lists.append(point_data_list)
                if request.form.get("showLines"):
                    kml_data_lists.append(line_data_list)
                if request.form.get("showPolygons"):
                    kml_data_lists.append(polygon_data_list)

                kml_file = export_to_kml.export_to_kml(topo_map_point_list + topo_map_interpolated_nodes, topo_map_line_list)
                #kml_file = export_to_kml.export_to_kml(kml_data_lists)

                kml_bytes = kml_file.encode('utf-8')
    
                # Creating BytesIO object to store the bytes
                kml_bytes_io = BytesIO()
                kml_bytes_io.write(kml_bytes)
                kml_bytes_io.seek(0)
    
                # Sending the file as an attachment
                return send_file(kml_bytes_io, as_attachment=True, attachment_filename=vineyard_id + '.kml', mimetype='application/vnd.google-earth.kml+xml')

        return render_template('vineyard_geojson_orion.html',
                            selected_vineyard_id=  selected_vineyard_id,
                            all_vineyard_data_list = all_vineyard_data_list,
                            vineyard_data_list = vineyard_data_list,
                            block_data_list = block_data_list,
                            block_area_data_list = block_area_data_list,
                            vine_row_data_list = vine_row_data_list,
                            vineyard_area =  round(vineyard_area, 2),
                            vineyard_total_rows = vineyard_total_rows,
                            vineyard_total_row_length = round(vineyard_total_row_length, 2),                            
                            under_vine_area = round(under_vine_area, 2),
                            mid_row_area = round(mid_row_area, 2),
                            vineyard_total_vines = vineyard_total_vines,
                            geojson_data = geojson_data, 
                            vine_row_boundaries = vine_row_boundaries,
                            )
    
    except S3Error as exc:
        return f"Error: {exc}"
    
@app.route('/jojo_geojson_file', methods=['GET', 'POST'])
def jojo_geojson_file():
    try:
        return render_template('jojo_geojson_file.html'                           
                               )

    except Exception as exc:
        return f"Error: {exc}"
    
@app.route('/import_csv', methods=['GET', 'POST'])
def import_csv():
    geojson_feature_collection={}
    try:
        if request.method == 'POST':            
            if 'upload_csv' in request.form:
                # Check if a file was uploaded
                if 'csv_file' not in request.files:
                    return 'No file uploaded', 400

                file = request.files['csv_file']

                # Check if the file has a valid extension
                if file.filename == '' or not file.filename.endswith('.csv'):
                    return 'Invalid file', 400

                # Generate GeoJSON from the DataFrame
                # if fileHasVineLocations
                if request.form.get("fileHasVineLocations"):
                    geojson_feature_collection = csv_rows_vines_upload_to_geojson.csv_to_geojson(file)
                else:
                    geojson_feature_collection = csv_upload_to_geojson.csv_to_geojson(file)

            print(geojson_feature_collection)

            # Update existing features with 'vine_row_id'
            for feature in geojson_feature_collection['features']:
                feature['properties']['vine_row_id'] = feature['properties']['Row']

            # if request.is_json:
            #     print("if request.is_json:")
            #     request_data = request.get_json()
            #     vineyard_id = request_data.get('vineyard_id')
            #     vineyard_name = request_data.get('vineyard_name')
            #     street_address = request_data.get('street_address')
            #     owner = request_data.get('owner')
            #     geojson_string = request_data['geojson_data']
                
            #     geojson_data = json.loads(geojson_string)

            #     # if all the vineyard variables are filled in save to orion
            #     if vineyard_id and vineyard_name and street_address and owner and geojson_feature_collection:
            #         print("if vineyard_id and vineyard_name and street_address and owner and filtered_geojson_data:")
            #         bounding_box = get_padded_bounding_box.get_padded_bounding_box(geojson_data, 10)

            #         # Create vineyard entity
            #         #orion_add_vineyard.create_vineyard_entity(vineyard_id, vineyard_name, street_address, owner, bounding_box)

            #         print("if vineyard_id and filtered_geojson_data: mapbox_to_orion")
            #         #mapbox_to_orion_csv.mapbox_to_orion_csv(vineyard_id, geojson_data)

            # # Iterate through the features to calculate midpoints and create new line strings
            # for i in range(len(geojson_feature_collection['features']) - 1):
            #     line1 = geojson_feature_collection['features'][i]['geometry']['coordinates']
            #     line2 = geojson_feature_collection['features'][i + 1]['geometry']['coordinates']
                
            #     midpoint_start = calculate_midpoint(line1[0], line2[0])
            #     midpoint_end = calculate_midpoint(line1[-1], line2[-1])
                
            #     new_line = {
            #         "type": "Feature",
            #         "geometry": {
            #             "type": "LineString",
            #             "coordinates": [midpoint_start, midpoint_end]
            #         },
            #         "properties": {
            #             "mid_row_line_id": f"{geojson_feature_collection['features'][i]['properties']['Row']}-{geojson_feature_collection['features'][i + 1]['properties']['Row']}"
            #         }
            #     }
                
            #     # Append the new line string to the original GeoJSON data
            #     geojson_feature_collection['features'].append(new_line)

        return render_template('import_csv.html',
                               geojson_feature_collection = geojson_feature_collection                               
                               )

    except Exception as exc:
        return f"Error: {exc}"
    
@app.route('/import_csv_click_points', methods=['GET', 'POST'])
def import_csv_click_points():
    geojson_feature_collection={}
    try:
        if request.method == 'POST':
            # Check if a file was uploaded
            if 'csv_file' not in request.files:
                return 'No file uploaded', 400

            file = request.files['csv_file']

            # Check if the file has a valid extension
            if file.filename == '' or not file.filename.endswith('.csv'):
                return 'Invalid file', 400

            # Generate GeoJSON from the DataFrame
            geojson_feature_collection = csv_upload_to_geojson.csv_to_geojson(file)

        return render_template('import_csv_click_points.html',
                               geojson_feature_collection = geojson_feature_collection                               
                               )

    except Exception as exc:
        return f"Error: {exc}"


@app.route('/import_csv_click_points_bearing', methods=['GET', 'POST'])
def import_csv_click_points_bearing():
    geojson_feature_collection={}
    try:
        if request.method == 'POST':
            # Check if a file was uploaded
            if 'csv_file' not in request.files:
                return 'No file uploaded', 400

            file = request.files['csv_file']

            # Check if the file has a valid extension
            if file.filename == '' or not file.filename.endswith('.csv'):
                return 'Invalid file', 400

            # Generate GeoJSON from the DataFrame
            geojson_feature_collection = csv_upload_to_geojson.csv_to_geojson(file)

        return render_template('import_csv_click_points_bearing.html',
                               geojson_feature_collection = geojson_feature_collection                               
                               )

    except Exception as exc:
        return f"Error: {exc}"

@app.route('/import_csv_click_points_bearing_select_points', methods=['GET', 'POST'])
def import_csv_click_points_bearing_select_points():
    geojson_feature_collection={}
    try:
        if request.method == 'POST':
            print("request.method == 'POST':")
            if 'upload_csv' in request.form:
                print("if 'upload_csv' in request.form:")
                # Check if a file was uploaded
                if 'csv_file' not in request.files:
                    return 'No file uploaded', 400
                else:
                    file = request.files['csv_file']

                # Check if the file has a valid extension
                if file.filename == '' or not file.filename.endswith('.csv'):
                    return 'Invalid file', 400

                # Generate GeoJSON from the DataFrame
                geojson_feature_collection = csv_upload_to_geojson.csv_to_geojson(file)

            if request.is_json:
                print("if request.is_json:")
                request_data = request.get_json()
                vineyard_id = request_data.get('vineyard_id')
                vineyard_name = request_data.get('vineyard_name')
                street_address = request_data.get('street_address')
                owner = request_data.get('owner')
                geojson_string = request_data['geojson_data']
                # print("vineyard_id: " + str(vineyard_id))
                # print("geojson_string: " + str(geojson_string))

                geojson_data = json.loads(geojson_string)

                # print("geojson_data: " + str(geojson_data))

                # geojson_features = geojson_data['features']

                # print("geojson_features: " + str(geojson_features))

                filtered_features = [feature for feature in geojson_data['features'] if feature["properties"].get("Point") != "End Point"]

                # Create a new GeoJSON object with the filtered features
                filtered_geojson_data = {
                    "type": "FeatureCollection",
                    "features": filtered_features
                }

                filtered_geojson_string = json.dumps(filtered_geojson_data)

                if vineyard_id and vineyard_name and street_address and owner and filtered_geojson_data:
                    print("if vineyard_id and vineyard_name and street_address and owner and filtered_geojson_data:")
                    bounding_box = get_padded_bounding_box.get_padded_bounding_box(filtered_geojson_string, 10)

                    # Create vineyard entity
                    orion_add_vineyard.create_vineyard_entity(vineyard_id, vineyard_name, street_address, owner, bounding_box)

                    print("if vineyard_id and filtered_geojson_data: mapbox_to_orion")
                    mapbox_to_orion_csv.mapbox_to_orion_csv(vineyard_id, filtered_geojson_string)
                else:
                    return 'Error: Missing data in request body.', 400

        return render_template('import_csv_click_points_bearing_select_points.html',
                                geojson_feature_collection = geojson_feature_collection
                               )

    except Exception as exc:
        return f"Error: {exc}"

@app.route('/create_map', methods=['GET', 'POST'])
def create_map():
    try:
        if request.method == 'POST':
            # Get data from the request
            vineyard_id = request.json.get('vineyard_id')
            geojson_data = request.json.get('geojson_data')

            # print("vineyard_id " + str(vineyard_id))
            # print("geojson_data " + str(geojson_data))

            mapbox_to_orion.mapbox_to_orion(vineyard_id, geojson_data)

        return render_template('create_map.html'                           
                               )

    except Exception as exc:
        return f"Error: {exc}"

@app.route('/view_geojson_file', methods=['GET', 'POST'])
def view_geojson_file():
    geojson_data = {
        "type": "FeatureCollection",
        "features": []
    }

    try:
        if request.method == 'POST':
            if 'upload_geojson' in request.form:
                # Check if a file was uploaded
                if 'file' not in request.files:
                    return 'No file uploaded', 400

                file = request.files['file']

                # Check if the file has a valid extension
                if file.filename == '' or not file.filename.endswith('.geojson'):
                    return 'Invalid file', 400

                # Read the content of the file and decode it
                file_content = file.read().decode('utf-8')

                # Parse the JSON content
                try:
                    geojson_data = json.loads(file_content)

                    # Update existing features with 'vine_row_id'
                    for feature in geojson_data['features']:
                        feature['properties']['vine_row_id'] = feature['properties']['Row']

                    # Iterate through the features to calculate midpoints and create new line strings
                    for i in range(len(geojson_data['features']) - 1):
                        line1 = geojson_data['features'][i]['geometry']['coordinates']
                        line2 = geojson_data['features'][i + 1]['geometry']['coordinates']
                        
                        midpoint_start = calculate_midpoint(line1[0], line2[0])
                        midpoint_end = calculate_midpoint(line1[-1], line2[-1])
                        
                        new_line = {
                            "type": "Feature",
                            "geometry": {
                                "type": "LineString",
                                "coordinates": [midpoint_start, midpoint_end]
                            },
                            "properties": {
                                "mid_row_line_id": f"{geojson_data['features'][i]['properties']['Row']}-{geojson_data['features'][i + 1]['properties']['Row']}"
                            }
                        }
                        
                        # Append the new line string to the original GeoJSON data
                        geojson_data['features'].append(new_line)

                except json.JSONDecodeError:
                    return 'Invalid JSON format', 400                   
            
            elif 'button_export_to_antobot_xml' in request.form: # If request is to export to antobot XML format
                geojson_data = request.form.get('geojson_data')
                geojson_data = json.loads(geojson_data)
                xml_file = export_geojson_to_antobot_xml.coordinates_to_xml(geojson_data, 1.0) # Takes geojson_data and row width and exports to antobot xml format
                xml_bytes = BytesIO(xml_file.encode())

                return send_file(xml_bytes, as_attachment=True, attachment_filename="antobot.xml", mimetype='text/plain')

        return render_template('view_geojson_file.html',
                               geojson_data = geojson_data
                               )

    except Exception as exc:
        return f"Error: {exc}"
    
@app.route('/import_mapvit', methods=['GET', 'POST'])
def import_mapvit():

    message = ""

    try:
        if request.method == 'POST':
            if 'upload_geojson' in request.form:
                # Check if a file was uploaded
                if 'file' not in request.files:
                    message = "No file uploaded"
                    return 'No file uploaded', 400

                file = request.files['file']

                # Check if the file has a valid extension
                if file.filename == '' or not file.filename.endswith('.geojson'):
                    message = "Invalid file"
                    return 'Invalid file', 400
                
                vineyard_id = request.form.get('vineyard_id')
                vine_spacing = request.form.get('vine_spacing')
                under_vine_width = request.form.get('under_vine_width')
                anchor_post_distance = request.form.get('anchor_post_distance')

                # Read the content of the file and decode it
                file_content = file.read().decode('utf-8')

                # Parse the JSON content
                try:
                    geojson_data = json.loads(file_content)

                    # mapvit_to_orion.mapvit_to_orion(geojson_data, vineyard_id, vine_spacing, under_vine_width, anchor_post_distance)

                    message = "Import Successful"

                except json.JSONDecodeError:
                    message = "Invalid JSON format"
                    return 'Invalid JSON format', 400

        return render_template('import_mapvit.html',
                               message = message
                               )

    except Exception as exc:
        return f"Error: {exc}"
    
@app.route('/edit_map', methods=['GET', 'POST'])
def edit_map():    
    vineyard_id = selected_vineyard_id = request.form.get('vineyard_id', 'jojo')  # Get the selected vineyard_id from the HTML form

    all_vineyard_data_list = []
    block_data_list = []
    vine_row_data_list = []
    point_data_list = []
    line_data_list = []
    polygon_data_list = []
    data = "data"

    try:
        if request.method == 'POST':
            # Get data from the request
            #geojson_data = request.json('geojson_data')
            data = request.json
        
            # Check if save_button_pressed is present and set to True
            # if data.get('save_button_pressed') == True:
            #     print("hello")

            #print("vineyard_id " + str(vineyard_id))
            #print("geojson_data " + str(geojson_data))

            # mapbox_to_orion.mapbox_to_orion(vineyard_id, geojson_data)

        # Query Orion to get ALL entities of type "Vineyard"
        fiware_orion_url_point = f"{FIWARE_ORION_BASE_URL}?type=Vineyard"
        all_vineyard_response = requests.get(fiware_orion_url_point)

        if all_vineyard_response.status_code == 200:
            all_vineyard_data = all_vineyard_response.json()
            for all_vineyard_entity in all_vineyard_data:
                all_id = all_vineyard_entity['id']
                all_vineyard_id = all_vineyard_entity['vineyard_id']['value']
                all_name = all_vineyard_entity['name']['value']
                all_street_address = all_vineyard_entity['street_address']['value']
                all_owner = all_vineyard_entity['owner']['value']
                all_coordinates = all_vineyard_entity['geom']['value']['coordinates']

                all_vineyard_data_list.append({'id': all_id, 'vineyard_id': all_vineyard_id, 'name': all_name, 'street_address': all_street_address,  'owner': all_owner, 'coordinates': all_coordinates, 'type': 'MultiPoint'})
        else:
            print(f"Failed to retrieve vineyard data. Status code: {all_vineyard_response.status_code}")

        # Query Orion to get all entities of type "point"
        fiware_orion_url_point = f"{FIWARE_ORION_BASE_URL}?type=point&q=vineyard_id=={vineyard_id}"
        point_response = requests.get(fiware_orion_url_point)

        if point_response.status_code == 200:
            point_data = point_response.json()
            for point_entity in point_data:
                point_id = point_entity['id']
                name = point_entity['name']['value']
                category = point_entity['category']['value']
                class_string = point_entity['class']['value']
                coordinates = point_entity['location']['value']['coordinates']

                point_data_list.append({'point_id': point_id, 'name': name, 'category': category, 'class_string': class_string, 'coordinates': coordinates, 'type': 'Point'})
        else:
            print(f"Failed to retrieve point data. Status code: {point_response.status_code}")

        # Query Orion to get all entities of type "line"
        fiware_orion_url_line = f"{FIWARE_ORION_BASE_URL}?type=line&q=vineyard_id=={vineyard_id}"
        line_response = requests.get(fiware_orion_url_line)

        if line_response.status_code == 200:
            line_data = line_response.json()
            for line_entity in line_data:
                line_id = line_entity['id']
                name = line_entity['name']['value']
                category = line_entity['category']['value']
                class_string = line_entity['class']['value']
                coordinates = line_entity['geom']['value']['coordinates']
                length = calculate_line_length(coordinates)

                line_data_list.append({'line_id': line_id, 'name': name, 'category': category, 'class_string': class_string, 'coordinates': coordinates, 'type': 'LineString'})
        else:
            print(f"Failed to retrieve line data. Status code: {line_response.status_code}")

        # Query Orion to get all entities of type "polygon"
        fiware_orion_url_polygon = f"{FIWARE_ORION_BASE_URL}?type=polygon&q=vineyard_id=={vineyard_id}"
        polygon_response = requests.get(fiware_orion_url_polygon)

        if polygon_response.status_code == 200:
            polygon_data = polygon_response.json()
            for polygon_entity in polygon_data:
                polygon_id = polygon_entity['id']
                name = polygon_entity['name']['value']
                category = polygon_entity['category']['value']
                class_string = polygon_entity['class']['value']
                coordinates = polygon_entity['geom']['value']['coordinates']
                area, perimeter = calculate_polygon_area(coordinates)

                polygon_data_list.append({'polygon_id': polygon_id, 'name': name, 'category': category, 'class_string': class_string, 'coordinates': coordinates, 'type': 'Polygon'})
        else:
            print(f"Failed to retrieve point data. Status code: {polygon_response.status_code}")

        # Query Orion to get all entities of type "VineRow"
        #fiware_orion_url_vine_row = f"{FIWARE_ORION_BASE_URL}?type=VineRow&offset=7&limit=92" # ?type=VineRow&limit=200"
        fiware_orion_url_vine_row = f"{FIWARE_ORION_BASE_URL}?type=VineRow&q=vineyard_id=={vineyard_id}&limit=200" # ?type=VineRow&limit=200"
        vine_row_response = requests.get(fiware_orion_url_vine_row)

        if vine_row_response.status_code == 200:
            vine_row_data = vine_row_response.json()
            for vine_row_entity in vine_row_data:
                vine_row_id = vine_row_entity['id']
                user_defined_id = vine_row_entity['user_defined_id']['value']
                block_id = vine_row_entity['block_id']['value']
                coordinates = vine_row_entity['geom']['value']['coordinates']
                anchor_post_distance = vine_row_entity['anchor_post_distance']['value']
                under_vine_width = vine_row_entity['under_vine_width']['value']
                vine_spacing = vine_row_entity['vine_spacing']['value']

                vine_row_data_list.append({'vine_row_id': vine_row_id, 'user_defined_id': user_defined_id, 'block_id': block_id, 'coordinates': coordinates, 'type': 'LineString'})
   
                # Sort the list based on user_defined_id values, depends on the user_defined_id having assending numbers
                vine_row_data_list = sorted(vine_row_data_list, key=lambda x: (int(re.search(r'\d+$', x['user_defined_id']).group()), x['user_defined_id']))

        else:
            print(f"Failed to retrieve vine_row data. Status code: {vine_row_response.status_code}")
          
        # Query Orion to get all entities of type "Block"
        fiware_orion_url_block = f"{FIWARE_ORION_BASE_URL}?type=Block&q=vineyard_id=={vineyard_id}&limit=200"
        block_response = requests.get(fiware_orion_url_block)

        if block_response.status_code == 200:
            block_data = block_response.json()
            for block_entity in block_data:
                block_id = block_entity['id']
                user_defined_id = block_entity['user_defined_id']['value']
                name = block_entity['name']['value']
                variety = block_entity['variety']['value']
                anchor_post_distance = vine_row_entity['anchor_post_distance']['value']
                under_vine_width = vine_row_entity['under_vine_width']['value']
                vine_spacing = vine_row_entity['vine_spacing']['value']
                coordinates = block_entity['geom']['value']['coordinates']                

                block_data_list.append({'block_id': block_id, 'user_defined_id': user_defined_id, 'name': name, 'variety': variety,'coordinates': coordinates, 
                                        'anchor_post_distance': anchor_post_distance, 'under_vine_width': under_vine_width, 'vine_spacing': vine_spacing,'type': 'Polygon'})
                                
        else:
            print(f"Failed to retrieve block data. Status code: {block_response.status_code}")

        data_lists = []
        data_lists.append(block_data_list)
        data_lists.append(vine_row_data_list)
        data_lists.append(point_data_list)
        data_lists.append(line_data_list)
        data_lists.append(polygon_data_list)

        geojson_data = export_to_geojson.create_geojson(data_lists)

        return render_template('edit_map.html',
                                selected_vineyard_id =  selected_vineyard_id,
                                all_vineyard_data_list = all_vineyard_data_list,
                                geojson_data = geojson_data,
                                data = data
                               )

    except Exception as exc:
        return f"Error: {exc}"
    
@app.route('/delete_entity', methods=['GET', 'POST'])
def delete_entity():
    all_entity_list = []

    # Query Orion to get ALL entities
    fiware_orion_url_point = f"{FIWARE_ORION_BASE_URL}?limit=1000"
    all_entity_response = requests.get(fiware_orion_url_point)

    if all_entity_response.status_code == 200:
        all_entity_data = all_entity_response.json()
        for all_entity in all_entity_data:
            all_id = all_entity.get('id', 'Unknown ID')
            vineyard_id = all_entity.get('vineyard_id', {}).get('value', 'Unknown Vineyard ID')
            user_defined_id = all_entity.get('user_defined_id', {}).get('value', 'Unknown User Defined ID')
            name = all_entity.get('name', {}).get('value', 'Unnamed Entity')
            type = all_entity.get('type', 'Unknown Type')

            all_entity_list.append({'id': str(all_id), 'vineyard_id': str(vineyard_id), 'user_defined_id': str(user_defined_id), 'name': str(name), 'type': str(type)})
    else:
        print(f"Failed to retrieve vineyard data. Status code: {all_entity_response.status_code}")

    try:
        if request.method == 'POST':
            # Get data from the request
            entity_id = request.form.get('entity_id')
            #print("Delete: " + str(entity_id))

            orion_delete_entity.delete_entity(entity_id)

        return render_template('delete_entity.html',
                               all_entity_list = all_entity_list
                               )

    except Exception as exc:
        return f"Error: {exc}"
    
@app.route('/import_geojson_file', methods=['GET', 'POST'])
def import_geojson_file():

    try:
        if request.method == 'POST':
            if 'upload_geojson' in request.form:
                # Check if a file was uploaded
                if 'file' not in request.files:
                    return 'No file uploaded', 400

                file = request.files['file']
                vineyard_id = request.form.get('vineyard_id')

                # Check if the file has a valid extension
                if file.filename == '' or not file.filename.endswith('.geojson'):
                    return 'Invalid file', 400

                # Read the content of the file and decode it
                file_content = file.read().decode('utf-8')

                # Parse the JSON content
                try:
                    geojson_data = json.loads(file_content)

                    geojson_to_orion.geojson_to_orion(geojson_data, vineyard_id)                    

                except json.JSONDecodeError:
                    return 'Invalid JSON format', 400

        return render_template('import_geojson_file.html'
                               )

    except Exception as exc:
        return f"Error: {exc}"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
